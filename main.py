from action import Action
from data_adaptor import DataAdaptor
from db_CodernityDB import DB_CodernityDB
from keyboard_monitor import KeyboardMonitor
from mgc import GC
from reward import Reward
from sound import Sound
from vision_screen import ScreenVision
from vision_video_file import VideoFileVision
import constants
import copy
import memory
import numpy as np
import status
import sys
import thread
import time
import util

sound = None
is_debug = False

try:
    print 'initializing, please wait.\n'
    DPS = 1.0 / constants.process_per_second
    data_adaptor = DataAdaptor(DB_CodernityDB(folder='data/CodernityDB/'))
    gc = GC(data_adaptor)
    reward = Reward()
    keyboard = KeyboardMonitor()
    thread.start_new_thread(keyboard.start, ())
    if len(sys.argv) == 2:
        file_path = sys.argv[1]
        vision = VideoFileVision(data_adaptor, file_path)
    else:
        vision = ScreenVision(data_adaptor)
    sound = Sound()
    memory.data_adaptor = data_adaptor
    actor = Action(data_adaptor)
    thread.start_new_thread(sound.receive, ())
    sequential_time_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
    working_memories = []
    frames = 0
    last_process_time = 0
    work_status = status.init_status()
    print 'initialized.\n'
    while 1:
        start = time.time()
        ts1 = time.time()

        key = keyboard.get_key()
        if key is constants.KEY_SHIFT:
            sound.start_thread = False
            break

        # print frames
        frames = frames + 1

        status.calculate_status(work_status, DPS, frames)

        ts2 = time.time()
        d1 = ts2 - ts1

        vision.process(working_memories, sequential_time_memories, work_status, key)

        ts3 = time.time()
        d2 = ts3 - ts2

        sound.process(working_memories, sequential_time_memories, work_status)
        # actor.process(working_memories, sequential_time_memories, work_status)

        ts4 = time.time()
        d3 = ts4 - ts3

        reward.process(sequential_time_memories, key)

        ts5 = time.time()
        d4 = ts5 - ts4

        memory.associate(working_memories)
        memory.prepare_expectation(working_memories)
        memory.check_expectation(working_memories, sequential_time_memories)

        ts6 = time.time()
        d5 = ts6 - ts5

        memory.compose(working_memories, sequential_time_memories)

        ts7 = time.time()
        d6 = ts7 - ts6

        # work end
        work_duration = util.time_diff(start)
        status.update_status(working_memories, work_status, work_duration)

        ts8 = time.time()
        d7 = ts8 - ts7

        working_memories = memory.cleanup_working_memories(working_memories, work_status)

        ts9 = time.time()
        d8 = ts9 - ts8

        process_duration = util.time_diff(start)
        gc.process(process_duration)

        ts10 = time.time()
        d9 = ts10 - ts9

        all_duration = util.time_diff(start)
        # print 'frame used time ', all_duration
        if is_debug and all_duration > 0.2:
            print 'used time detail ', np.around([d1, d2, d3, d4, d5, d6, d7, d8, d9], decimals=2)

        # all end, sleep to avoid running too fast
        if all_duration < DPS:
            time.sleep(DPS - all_duration)
        elif (last_process_time + all_duration) < DPS * 2:
            time.sleep(DPS * 2 - last_process_time - all_duration)

        last_process_time = all_duration


except KeyboardInterrupt:
    print("quiting...")
    sound.start_thread = False
