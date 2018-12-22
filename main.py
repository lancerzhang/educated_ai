from data_adaptor import DataAdaptor
from db_CodernityDB import DB_CodernityDB
from db_tinydb import DB_TinyDB
from tinydb import TinyDB
from vision_screen import ScreenVision
from vision_video_file import VideoFileVision
import actor
import copy
import cv2
import memory
import sound
import status
import sys
import thread
import time
import util

# number of process per second
PPS = 10
# duration per process (s)
DPS = 1.0 / PPS

try:
    print 'wake up.\n'
    # _data = Data(DB_TinyDB(TinyDB('TinyDB.json')))
    data_service = DataAdaptor(DB_CodernityDB(folder='data/CodernityDB/'))
    if len(sys.argv) == 2:
        file_path = sys.argv[1]
        vision = VideoFileVision(data_service, file_path)
    else:
        vision = ScreenVision(data_service)
    memory.data_service = data_service
    actor.data_service = data_service
    thread.start_new_thread(sound.receive, ())
    sequential_time_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
    working_memories = []
    frames = 0
    work_status = status.init_status(PPS)
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

        if frames % (PPS * 15) == 0:
            data_service.full_housekeep()
        if frames % (PPS * 1) == 0:
            data_service.partial_housekeep()

        # print 'frame used time	' + str(time.time() - start)

        # all end, sleep to avoid running too fast
        all_duration = util.time_diff(start)
        if all_duration < DPS:
            time.sleep(DPS - all_duration)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


except KeyboardInterrupt:
    print("quiting...")
    sound.start_thread = False
    # data_service.start_thread = False
