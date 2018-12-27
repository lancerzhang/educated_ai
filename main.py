from data_adaptor import DataAdaptor
from db_CodernityDB import DB_CodernityDB
from db_tinydb import DB_TinyDB
from mgc import GC
from tinydb import TinyDB
from sound import Sound
from vision_screen import ScreenVision
from vision_video_file import VideoFileVision
import actor
import constants
import copy
import cv2
import memory
import numpy as np
import status
import sys
import thread
import time
import util

sound = None

try:
    print 'initializing, please wait.\n'
    DPS = 1.0 / constants.process_per_second
    # _data = Data(DB_TinyDB(TinyDB('TinyDB.json')))
    data_adaptor = DataAdaptor(DB_CodernityDB(folder='data/CodernityDB/'))
    gc = GC(data_adaptor)
    if len(sys.argv) == 2:
        file_path = sys.argv[1]
        vision = VideoFileVision(data_adaptor, file_path)
    else:
        vision = ScreenVision(data_adaptor)
    sound = Sound(data_adaptor)
    memory.data_adaptor = data_adaptor
    actor.data_adaptor = data_adaptor
    thread.start_new_thread(sound.receive, ())
    sequential_time_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
    working_memories = []
    frames = 0
    last_process_time = 0
    work_status = status.init_status()
    print 'initialized.\n'
    while 1:
        start = time.time()
        # print frames
        frames = frames + 1

        status.calculate_status(work_status, DPS, frames)

        vision.process(working_memories, sequential_time_memories, work_status)
        sound.process(working_memories, sequential_time_memories, work_status)
        # actor.process(working_memories, sequential_time_memories, work_status)

        memory.associate(working_memories)
        memory.prepare_expectation(working_memories)

        memory.check_expectation(working_memories, sequential_time_memories)
        memory.compose(working_memories, sequential_time_memories)

        # work end
        work_duration = util.time_diff(start)
        status.update_status(working_memories, work_status, work_duration)

        working_memories = memory.cleanup_working_memories(working_memories, work_status)

        process_duration = util.time_diff(start)
        gc.process(process_duration)

        print 'frame used time	' + str(time.time() - start)

        # all end, sleep to avoid running too fast
        all_duration = util.time_diff(start)
        if all_duration < DPS:
            time.sleep(DPS - all_duration)
        elif (last_process_time + all_duration) < DPS * 2:
            time.sleep(DPS * 2 - last_process_time - all_duration)

        last_process_time = all_duration

        if cv2.waitKey(1) & 0xFF == ord('q'):
            sound.start_thread = False
            break


except KeyboardInterrupt:
    print("quiting...")
    sound.start_thread = False
# data_service.start_thread = False
