from action import Action
from data_adaptor import DataAdaptor
from db_CodernityDB import DB_CodernityDB
from keyboard_monitor import KeyboardMonitor
from mgc import GC
from sound import Sound
from vision_screen import ScreenVision
from vision_video_file import VideoFileVision
import constants
import copy
import memory
import reward
import status
import sys
import thread
import time
import util

sound = None

try:
    print 'initializing, please wait.\n'
    DPS = 1.0 / constants.process_per_second
    data_adaptor = DataAdaptor(DB_CodernityDB(folder='data/CodernityDB/'))
    gc = GC(data_adaptor)
    keyboard = KeyboardMonitor()
    thread.start_new_thread(keyboard.start, ())
    if len(sys.argv) == 2:
        file_path = sys.argv[1]
        vision = VideoFileVision(data_adaptor, file_path)
    else:
        vision = ScreenVision(data_adaptor)
    sound = Sound(data_adaptor)
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
        # print frames
        frames = frames + 1

        status.calculate_status(work_status, DPS, frames)

        vision.process(working_memories, sequential_time_memories, work_status)
        sound.process(working_memories, sequential_time_memories, work_status)
        # actor.process(working_memories, sequential_time_memories, work_status)

        key = keyboard.get_key()
        if key is constants.KEY_SHIFT:
            sound.start_thread = False
            break
        reward.process(sequential_time_memories, key)

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


except KeyboardInterrupt:
    print("quiting...")
    sound.start_thread = False
