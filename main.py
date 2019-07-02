from components.action import Action
from components.bio_memory import BioMemory
from components.data_adaptor import DataAdaptor
from components.data_sqlite3 import DataSqlite3
from components.keyboard_listener import KeyboardListener
from components.mouse_listener import MouseListener
from components.mgc import GC
from components.reward import Reward
from components.sound_microphone import MicrophoneSound
from components.sound_video_file import VideoFileSound
from components.status import Status
from components.vision_screen import ScreenVision
from components.vision_video_file import VideoFileVision
from components import constants, util
import getopt
import logging
import numpy as np
import sys
import threading
import time

logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s %(thread)d %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')

MAIN_CONFIG_FILE = 'data/main.npy'


def load_main_conf():
    try:
        configs = np.load(MAIN_CONFIG_FILE)
    except IOError:
        configs = None
    return configs


def save_main_config():
    config = {constants.LAST_SYSTEM_TIME: time.time()}
    np.save(MAIN_CONFIG_FILE, np.array([config]))


def save_for_exit(mgc, sound):
    save_main_config()
    logging.info('saved and exiting...')
    if mgc:
        mgc.running = False
    if sound is MicrophoneSound:
        sound.running = False


def main(argv):
    is_hibernate = None
    video_file = None

    try:
        opts, args = getopt.getopt(argv, "hi:v:", ["hibernate=", "video="])
    except getopt.GetoptError:
        print('-i <hibernate> -v <video>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('-i <hibernate> -v <video>')
            sys.exit()
        elif opt in ("-i", "--hibernate"):
            is_hibernate = arg
        elif opt in ("-v", "--video"):
            video_file = arg

    try:
        logging.info('initializing, please wait.')
        dps = 1.0 / constants.process_per_second
        da = DataAdaptor(DataSqlite3('data/dump.sql'))
        bm = BioMemory(da)
        if is_hibernate and is_hibernate == 'yes':
            configs = load_main_conf()
            if configs:
                da.synchronize_memory_time(configs[0][constants.LAST_SYSTEM_TIME])
        mgc = GC()
        # use separate thread to prepare gc
        threading.Thread(target=mgc.prepare).start()
        reward_controller = Reward(bm)
        mouse_listener = MouseListener()
        keyboard_listener = KeyboardListener()
        mouse_thread = threading.Thread(target=mouse_listener.run)
        mouse_thread.daemon = True
        mouse_thread.start()
        keyboard_thread = threading.Thread(target=keyboard_listener.run)
        keyboard_thread.daemon = True
        keyboard_thread.start()
        status_controller = Status(bm)
        if video_file:
            vision_controller = VideoFileVision(bm, video_file, status_controller)
            sound_controller = VideoFileSound(bm, video_file)
        else:
            vision_controller = ScreenVision(bm)
            sound_controller = MicrophoneSound(bm)
            threading.Thread(target=sound_controller.receive).start()
            # _thread.start_new_thread(sound_controller.receive, ())
        action_controller = Action(bm)
        frames = 0
        last_process_time = 0
        logging.info('initialized.')
        print('initialized.')
        while 1:
            start = time.time()
            button = mouse_listener.get_button()
            key = keyboard_listener.get_key()
            if key is constants.KEY_SHIFT:
                # da.persist()
                save_for_exit(mgc, sound_controller)
                break

            logging.debug('frame is {0} '.format(frames))
            frames = frames + 1

            status_controller.calculate_status(dps, frames)
            bm.associate()
            bm.prepare_matching_virtual_memories()
            focus = vision_controller.process(status_controller, key)
            sound_controller.process(status_controller)
            action_controller.process(status_controller, button, focus)
            reward_controller.process(key)
            bm.check_matching_virtual_memories()
            bm.compose()

            # work end
            work_duration = util.time_diff(start)
            status_controller.update_status(work_duration)
            bm.cleanup_working_memories()

            process_duration = util.time_diff(start)
            # because sqlite3 multi-thread are difficult to handle concurrent issue
            mgc.execute()
            all_duration = util.time_diff(start)
            logging.info('frame used time {0} '.format(all_duration))

            # all end, sleep to avoid running too fast
            if all_duration < dps:
                time.sleep(dps - all_duration)
            elif (last_process_time + all_duration) < dps * 2:
                time.sleep(dps * 2 - last_process_time - all_duration)
            last_process_time = all_duration

    except KeyboardInterrupt:
        save_for_exit()


if __name__ == "__main__":
    main(sys.argv[1:])
