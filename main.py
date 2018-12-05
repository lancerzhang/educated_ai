import time, util, memory, vision, status, sound, copy, actor, constants
from data import Data
from tinydb import TinyDB
from db_tinydb import DB_TinyDB
from db_CodernityDB import DB_CodernityDB

# number of process per second
PPS = 10
# duration per process (s)
DPS = 1.0 / PPS

# _data = Data(DB_TinyDB(TinyDB('TinyDB.json')))
_data = Data(DB_CodernityDB())
memory.data = _data
vision.data = _data
actor.data = _data

try:
    print 'wake up.\n'
    # to group them as a new memory by time sequence
    sequential_time_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
    working_memories = []
    work_status = {}
    frames = 0
    while 1:
        # print frames
        frames = frames + 1
        start = time.time()

        status.calculate_status(work_status, PPS, frames)

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

except KeyboardInterrupt:
    print("quiting...")
    _data.housekeep()
