import getopt
import logging
import sys
import time
import traceback

from src import constants
from src.brain import Brain
from src.speech_microphone import MicrophoneSpeech
from src.speech_video_file import VideoFileSpeech
from src.vision_screen import ScreenVision
from src.vision_video_file import VideoFileVision

logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s %(threadName)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')


def print_info(brain):
    # print(f'len brain.memory_cache speech: {len(brain.memory_cache[constants.speech])}')
    print(f'len brain.all_memories speech: {len(brain.categorized_memory[constants.speech])}')
    print(f'len brain.all_memories pack: {len(brain.categorized_memory[constants.instant])}')
    print(f'len brain.all_memories temporal: {len(brain.categorized_memory[constants.temporal])}')
    # print(f'len brain.all_memories long: {len(brain.categorized_memory[constants.long])}')
    # print(f'stability is: {[x.stability for x in brain.all_memories.copy().values()]}')
    print(f'stability of speech is:'
          f' {[x.stability for x in brain.categorized_memory[constants.speech].copy().values()]}')
    print(f'stability of pack is:'
          f' {[x.stability for x in brain.categorized_memory[constants.instant].copy().values()]}')
    print(f'stability of temporal is:'
          f' {[x.stability for x in brain.categorized_memory[constants.temporal].copy().values()]}')
    # print(f'stability of long is:'
    #       f' {[x.stability for x in brain.categorized_memory[constants.long].copy().values()]}')
    # print(
    #     f'live time of speech is: {[int(time.time() - x.CREATED_TIME) for x in brain.categorized_memory[constants.speech].copy().values()]}')
    # print(
    #     f'live time of pack is: {[int(time.time() - x.CREATED_TIME) for x in brain.categorized_memory[constants.pack].copy().values()]}')
    # print(
    #     f'live time of instant is: {[int(time.time() - x.CREATED_TIME) for x in brain.categorized_memory[constants.instant].copy().values()]}')
    # print(
    #     f'live time of short is: {[int(time.time() - x.CREATED_TIME) for x in brain.categorized_memory[constants.short].copy().values()]}')
    # print(
    #     f'live time of long is: {[int(time.time() - x.CREATED_TIME) for x in brain.categorized_memory[constants.long].copy().values()]}')
    print(f'data len of pack is:'
          f' {[len(x.data) for x in brain.categorized_memory[constants.instant].copy().values()]}')
    print(f'data len of temporal is:'
          f' {[len(x.data) for x in brain.categorized_memory[constants.temporal].copy().values()]}')


def main(argv):
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
        elif opt in ('-v', '--video'):
            video_file = arg
        elif opt in ('-s', '--show'):
            is_show = arg

    try:
        logging.info('initializing, please wait.')
        brain = Brain()
        brain.start()
        brain.load()
        process_time = 1 / constants.process_per_second
        if video_file:
            vision = VideoFileVision(video_file, is_show)
            speech = VideoFileSpeech(video_file)
        else:
            vision = ScreenVision(brain)
            speech = MicrophoneSpeech(brain)
        speech.start()
        start_time = time.time()
        last_debug_time = time.time()
        logging.info('initialized.')
        print('initialized.')
        while 1:
            process_start = time.time()
            brain.prepare_frame()
            # logging.debug('frame started.')
            speech_features_serial = speech.process()
            vision_features = vision.process()
            # print(f'n speech_features_set {len(speech_features_set)}')
            # if (time.time() - start_time) > 10:
            #     print('here')
            brain.receive_speech(speech_features_serial)
            brain.receive_vision(vision_features)
            brain.recognize()
            # if (time.time() - start_time) > 20:
            #     speech.stop()
            process_end = time.time()
            idle_time = process_time - (process_end - process_start)
            # logging.debug(f'idle time {idle_time}')
            print(f'idle time {idle_time}')
            if idle_time > 0:
                time.sleep(idle_time)

            if time.time() - last_debug_time > 30:
                print_info(brain)
                last_debug_time = time.time()
                print(f'elapse time {time.time() - start_time}')

    except:
        logging.error(traceback.format_exc())


if __name__ == '__main__':
    main(sys.argv[1:])
