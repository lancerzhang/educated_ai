import getopt
import logging
import sys
import time
import traceback

from components import constants
from components.brain import Brain
from components.voice_microphone import MicrophoneVoice
from components.voice_video_file import VideoFileVoice
from components.vision_screen import ScreenVision
from components.vision_video_file import VideoFileVision

logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s %(threadName)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')


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
        process_time = 1 / constants.process_per_second
        if video_file:
            vision = VideoFileVision(video_file, is_show)
            voice = VideoFileVoice(video_file)
        else:
            vision = ScreenVision(brain)
            voice = MicrophoneVoice(brain)
        voice.start()
        start_time = time.time()
        logging.info('initialized.')
        print('initialized.')
        while 1:
            process_start = time.time()
            # logging.debug('frame started.')
            voice_pieces = voice.process()
            print(f'n features {len(voice_pieces)}')
            for piece in voice_pieces:
                brain.input_real(piece)
            process_end = time.time()
            idle_time = process_time - (process_end - process_start)
            # logging.debug(f'idle time {idle_time}')
            # print(f'idle time {idle_time}')
            if idle_time > 0:
                time.sleep(idle_time)
            print(f'elapse time {time.time() - start_time}')
    except:
        logging.error(traceback.format_exc())


if __name__ == '__main__':
    main(sys.argv[1:])
