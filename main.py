import getopt
import logging
import sys
import threading
import time
import traceback

import numpy as np
import schedule

from components import constants
from components import util
from components.action import Action
from components.brain import Brain
from components.favor import Favor
from components.keyboard_listener import KeyboardListener
from components.mouse_listener import MouseListener
from components.reward import Reward
from components.sound_microphone import MicrophoneSound
from components.sound_video_file import VideoFileSound
from components.status import Status
from components.vision_screen import ScreenVision
from components.vision_video_file import VideoFileVision

logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s %(threadName)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')

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


def save_for_exit(sound):
    save_main_config()
    logging.info('saved and exiting...')
    if sound is MicrophoneSound:
        sound.running = False


def run_pending():
    while 1:
        schedule.run_pending()
        time.sleep(1)


def main(argv):
    is_hibernate = None
    video_file = None
    is_show = None

    try:
        opts, args = getopt.getopt(argv, 'hi:v:s:', ['hibernate=', 'video=', 'show='])
    except getopt.GetoptError:
        print('error get options, should be -i <hibernate> -v <video> -s <show>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('-i <hibernate> -v <video> -s <show>')
            sys.exit()
        elif opt in ('-i', '--hibernate'):
            is_hibernate = arg
        elif opt in ('-v', '--video'):
            video_file = arg
        elif opt in ('-s', '--show'):
            is_show = arg

    try:
        logging.info('initializing, please wait.')
        dps = 1.0 / constants.process_per_second
        brain = Brain()
        brain.load()
        favor = Favor()
        favor.load()
        # TODO
        # if is_hibernate and is_hibernate == 'yes':
        #     configs = load_main_conf()
        #     if configs:
        #         da.synchronize_memory_time(configs[0][constants.LAST_SYSTEM_TIME])
        # schedule.every(89).seconds.do(brain.save)
        # schedule.every(10).seconds.do(brain.log_dashboard)
        schedule.every(60).seconds.do(favor.save)
        schedule_thread = threading.Thread(target=run_pending)
        schedule_thread.daemon = True
        schedule_thread.start()
        persist_thread = threading.Thread(target=brain.persist)
        persist_thread.daemon = True
        persist_thread.start()
        reward = Reward(brain)
        status = Status(brain)
        action = Action(brain)
        if video_file:
            vision = VideoFileVision(brain, favor, video_file, status, is_show)
            sound = VideoFileSound(brain, favor, video_file)
        else:
            vision = ScreenVision(brain, favor)
            sound = MicrophoneSound(brain, favor)
            sound_thread = threading.Thread(target=sound.receive)
            sound_thread.daemon = True
            sound_thread.start()
        mouse_listener = MouseListener()
        mouse_thread = threading.Thread(target=mouse_listener.run)
        mouse_thread.daemon = True
        mouse_thread.start()
        keyboard_listener = KeyboardListener()
        keyboard_thread = threading.Thread(target=keyboard_listener.run)
        keyboard_thread.daemon = True
        keyboard_thread.start()
        frames = 0
        last_process_time = 0
        logging.info('initialized.')
        print('initialized.')
        while 1:
            logging.info('frame started.')
            start = time.time()
            button = mouse_listener.get_button()
            key = keyboard_listener.get_key()
            if is_show is not 'n' and key is constants.KEY_SHIFT:
                brain.save()
                favor.save()
                save_for_exit(sound)
                break

            logging.debug('frame is {0} '.format(frames))
            frames = frames + 1

            # status.calculate_status(dps, frames)
            brain.associate()
            brain.activate_children()
            focus = vision.process(status, key)
            sound.process(status)
            if is_show is not 'n':
                action.process(button, focus)
            reward.process(key)
            brain.match_memories()
            vision.reproduce()
            brain.compose_memories()

            # work end
            work_duration = util.time_diff(start)
            # status_controller.update_status(work_duration)
            brain.post_matched_memories()
            brain.cleanup_active_memories()

            all_duration = util.time_diff(start)
            duration_ms = all_duration * 1000
            if duration_ms > 100:
                logging.info('frame took %d ms' % duration_ms)
            else:
                logging.debug('frame took %d ms' % duration_ms)

            # all end, sleep to avoid running too fast
            if all_duration < dps:
                time.sleep(dps - all_duration)
            elif (last_process_time + all_duration) < dps * 2:
                time.sleep(dps * 2 - last_process_time - all_duration)
            last_process_time = all_duration

    except KeyboardInterrupt:
        save_for_exit(None)
    except:
        logging.error(traceback.format_exc())


if __name__ == '__main__':
    main(sys.argv[1:])
