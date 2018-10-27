import time, util, memory, collections, vision, status, sound, copy
import numpy as np
from db import Database
from tinydb import TinyDB, Query

# number of process per second
PPS = 10
# duration per process (s)
DPS = 1.0 / PPS

# to group them as a new memory by time sequence
sequential_time_memories = {}

working_memories = []

work_status = {}

frames = 0
db = Database(TinyDB('TinyDB.json'))
memory.db = db

try:
    print 'wake up.\n'
    sequential_time_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
    while 1:
        frames = frames + 1
        start = time.time()

        status.calculate_status(work_status, DPS, frames)

        memory.associate(working_memories)
        memory.prepare_expectation(working_memories)

        vision.process(working_memories, work_status, sequential_time_memories)
        sound.process(working_memories, work_status, sequential_time_memories)

        memory.check_expectation(working_memories, sequential_time_memories)
        memory.compose(sequential_time_memories)

        # if watch result is the same for xxx, trigger a random move, 1/16 d, 0.1-0.5 s
        vision.move()
        # all end
        duration = util.time_diff(start)
        status.update_states(work_status, duration, working_memories)

        if not work_status[status.BUSY][status.MEDIUM_DURATION]:
            working_memories = memory.cleanup_working_memories(working_memories, work_status)

except KeyboardInterrupt:
    print("quiting...")
    db.housekeep()
