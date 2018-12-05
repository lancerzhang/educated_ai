import time, util, memory, vision, status, sound, copy, actor, constants,thread
from data_service import DataService
from tinydb import TinyDB
from db_tinydb import DB_TinyDB
from db_CodernityDB import DB_CodernityDB

# number of process per second
PPS = 5
# duration per process (s)
DPS = 1.0 / PPS

# _data = Data(DB_TinyDB(TinyDB('TinyDB.json')))
data_service = DataService(DB_CodernityDB())
memory.data_service = data_service
vision.data_service = data_service
actor.data_service = data_service

try:
    print 'wake up.\n'
    thread.start_new_thread(sound.receive, ())
    # to group them as a new memory by time sequence
    sequential_time_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
    working_memories = []
    work_status = {}
    frames = 0
    status.init_status(work_status,PPS)
    while 1:
        start = time.time()
        # print frames
        frames = frames + 1

        print working_memories
        status.calculate_status(work_status, DPS, frames)

        memory.associate(working_memories)
        memory.prepare_expectation(working_memories)

        vision.process(working_memories, work_status, sequential_time_memories)
        sound.process(working_memories, work_status, sequential_time_memories)
        actor.process(working_memories, work_status, sequential_time_memories)

        memory.check_expectation(working_memories, sequential_time_memories)
        memory.compose(sequential_time_memories)

        vision.process(working_memories, work_status, sequential_time_memories)
        sound.process(working_memories, work_status, sequential_time_memories)

        # all end
        duration = util.time_diff(start)
        status.update_status(work_status, duration, working_memories)

        if not work_status[constants.BUSY][constants.MEDIUM_DURATION]:
            working_memories = memory.cleanup_working_memories(working_memories, work_status)

        # print 'frame used time	' + str(time.time() - start)

except KeyboardInterrupt:
    print("quiting...")
    sound.start_thread = False
    data_service.housekeep()
