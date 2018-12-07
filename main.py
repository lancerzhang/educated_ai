import time, util, memory, vision, status, sound, copy, actor, constants, thread
from data_service import DataService
from tinydb import TinyDB
from db_tinydb import DB_TinyDB
from db_CodernityDB import DB_CodernityDB

# number of process per second
PPS = 10
# duration per process (s)
DPS = 1.0 / PPS

# _data = Data(DB_TinyDB(TinyDB('TinyDB.json')))
data_service = DataService(DB_CodernityDB(folder='data/CodernityDB/'))
memory.data_service = data_service
vision.data_service = data_service
actor.data_service = data_service

try:
    print 'wake up.\n'
    thread.start_new_thread(sound.receive, ())
    # to group them as a new memory by time sequence
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
        actor.process(working_memories, sequential_time_memories, work_status)

        memory.associate(working_memories)
        memory.prepare_expectation(working_memories)

        memory.check_expectation(working_memories, sequential_time_memories)
        memory.compose(working_memories, sequential_time_memories)

        # all end
        duration = util.time_diff(start)
        status.update_status(working_memories, work_status, duration)

        working_memories = memory.cleanup_working_memories(working_memories, work_status)
        if frames % (PPS * 60) == 0:
            data_service.housekeep()
        print 'frame used time	' + str(time.time() - start)
        print 'working_memories size ' + str(len(working_memories))

except KeyboardInterrupt:
    print("quiting...")
    sound.start_thread = False
    data_service.housekeep()
