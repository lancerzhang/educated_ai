from action import Action
from data_adaptor import DataAdaptor
from db_CodernityDB import DB_CodernityDB
from keyboard_listener import KeyboardListener
from mouse_listener import MouseListener
from mgc import GC
from reward import Reward
from sound import Sound
from vision_screen import ScreenVision
from vision_video_file import VideoFileVision
import constants
import copy
import getopt
import logging
import memory
import numpy as np
import status
import sys
import thread
import time
import util

logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

DATA_FOLDER = 'data/CodernityDB/'
MAIN_CONFIG_FILE = 'data/main.npy'
sound = None
vision = None


def load_main_conf():
    try:
        configs = np.load(MAIN_CONFIG_FILE)
    except IOError:
        configs = None
    return configs


def save_main_config():
    config = {constants.LAST_SYSTEM_TIME: time.time()}
    np.save(MAIN_CONFIG_FILE, np.array([config]))


def save_for_exit():
    save_main_config()
    if sound:
        sound.save_files()
        sound.start_thread = False
    if vision:
        vision.save_files()


def main(argv):
    is_hibernate = None
    video_file = None

    try:
        opts, args = getopt.getopt(argv, "hi:v:", ["hibernate=", "video="])
    except getopt.GetoptError:
        print '-i <hibernate> -v <video>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print '-i <hibernate> -v <video>'
            sys.exit()
        elif opt in ("-i", "--hibernate"):
            is_hibernate = arg
        elif opt in ("-v", "--video"):
            video_file = arg

    try:
        logging.info('initializing, please wait.')
        dps = 1.0 / constants.process_per_second
        data_adaptor = DataAdaptor(DB_CodernityDB(folder=DATA_FOLDER))
        if is_hibernate is None or is_hibernate is 'yes':
            configs = load_main_conf()
            if configs:
                data_adaptor.synchronize_memory_time(configs[0][constants.LAST_SYSTEM_TIME])
        gc = GC(data_adaptor)
        reward_controller = Reward()
        mouse_listener = MouseListener()
        keyboard_listener = KeyboardListener()
        thread.start_new_thread(mouse_listener.start, ())
        thread.start_new_thread(keyboard_listener.start, ())
        if video_file:
            vision_controller = VideoFileVision(data_adaptor, video_file)
        else:
            vision_controller = ScreenVision(data_adaptor)
        sound_controller = Sound()
        memory.data_adaptor = data_adaptor
        action_controller = Action(data_adaptor)
        thread.start_new_thread(sound_controller.receive, ())
        sequential_time_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
        working_memories = []
        frames = 0
        last_process_time = 0
        work_status = status.init_status()
        logging.info('initialized.')
        while 1:
            start = time.time()
            button = mouse_listener.get_button()
            key = keyboard_listener.get_key()
            if key is constants.KEY_SHIFT:
                save_for_exit()
                break

            logging.debug('frame is {0} '.format(frames))
            frames = frames + 1

            status.calculate_status(work_status, dps, frames)
            memory.associate(working_memories)
            memory.prepare_expectation(working_memories)
            vision_controller.process(working_memories, sequential_time_memories, work_status, key)
            sound_controller.process(working_memories, sequential_time_memories, work_status)
            action_controller.process(working_memories, sequential_time_memories, work_status, button)
            reward_controller.process(sequential_time_memories, key)
            memory.check_expectations(working_memories, sequential_time_memories)
            memory.compose(working_memories, sequential_time_memories)

            # work end
            work_duration = util.time_diff(start)
            status.update_status(working_memories, work_status, work_duration)
            working_memories = memory.cleanup_working_memories(working_memories)

            process_duration = util.time_diff(start)
            gc.process(process_duration)

            all_duration = util.time_diff(start)
            logging.debug('frame used time {0} '.format(all_duration))

            # all end, sleep to avoid running too fast
            if all_duration < dps:
                time.sleep(dps - all_duration)
            elif (last_process_time + all_duration) < dps * 2:
                time.sleep(dps * 2 - last_process_time - all_duration)
            last_process_time = all_duration

    except KeyboardInterrupt:
        logging.info('exit...')
        save_for_exit()


if __name__ == "__main__":
    main(sys.argv[1:])
