from src.action import Action
from src.brain import Brain
from src.favor import Favor
from src.keyboard_listener import KeyboardListener
from src.mouse_listener import MouseListener
from src.reward import Reward
from src.voice_microphone import MicrophoneVoice
from src.vision_cozmo import CozmoVision
from src.status import Status
from src import constants
from src import util
import logging
import schedule
import threading
import time
import traceback

logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s %(threadName)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')


def save_for_exit(vision, sound):
    logging.info('saved and exiting...')
    vision.running = False
    sound.running = False


def run_pending():
    while 1:
        schedule.run_pending()
        time.sleep(1)


def main():
    try:
        logging.info('initializing, please wait.')
        dps = 1.0 / constants.process_per_second
        brain = Brain()
        brain.load()
        favor = Favor()
        favor.load()
        schedule.every(5).seconds.do(brain.save)
        schedule.every(59).seconds.do(favor.save)
        schedule_thread = threading.Thread(target=run_pending)
        schedule_thread.daemon = True
        schedule_thread.start()
        reward = Reward(brain)
        status = Status(brain)
        action = Action(brain)
        vision = CozmoVision(brain, favor)
        vision_thread = threading.Thread(target=vision.run_cozmo_thread)
        vision_thread.daemon = True
        vision_thread.start()
        sound = MicrophoneVoice(brain, favor)
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
            while vision.ready:
                print(f'cozmo is ready')
                logging.info('frame started.')
                start = time.time()
                button = mouse_listener.get_button()
                key = keyboard_listener.get_key()
                if key is constants.KEY_SHIFT:
                    brain.save()
                    favor.save()
                    save_for_exit(vision, sound)
                    break

                logging.debug('frame is {0} '.format(frames))
                frames = frames + 1

                # brain.associate()
                # brain.activate_children()
                focus = vision.process(status, key)
                # sound.process(status)
                # action.process(status, button, focus)
                # reward.process(key)
                # brain.match_memories()
                # brain.compose_memories()
                # brain.cleanup()

                all_duration = util.time_diff(start)
                logging.info('frame took %d ms' % (all_duration * 1000))

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


if __name__ == "__main__":
    main()
