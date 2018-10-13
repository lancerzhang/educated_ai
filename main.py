import time, util, memory, collections, vision, expectation, sound, copy
import numpy as np
from db import Database
from tinydb import TinyDB, Query

# number of process per second
PPS = 10
# duration per process (s)
DPS = 1.0 / PPS

# expect working memories will match experience memories, if not, working memories will became new experience.
experience_memory = 0
# working memories are reflection of the environment, can find out state from few working memories
working_instant_memory_vision = np.zeros(5)  # last 0.5s
# vision array
# focus array
# mouse action array

# status - new, matching, matched
expectations = {}
slice_expectations = {}

working_memories = {}
# new_working_memories = []
total_matched_counts = [0, 0, 0]
fifo_list_durations2s = [0] * 2 * PPS
fifo_list_durations15s = [0] * 15 * PPS
fifo_list_durations60s = [0] * 60 * PPS
frames = 0
db = Database(TinyDB('TinyDB.json'))
memory.db = db

try:
    print 'wake up.\n'
    working_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_DICT)
    while 1:
        frames = frames + 1
        start = time.time()
        less_workload = False

        # cater startup time
        if frames > len(fifo_list_durations2s) and util.avg(fifo_list_durations2s) < DPS:
            less_workload = True

        if sum(total_matched_counts) == 0 or slice_expectations.empyt():
            vision.watch()
            sound.listen()
        else:
            vision.watch(slice_expectations)
            sound.hear(slice_expectations)
            total_matched_count = 0
            # loop  expectations, find out slice_expectations
            for exp in expectations:
                expectation.prepare_expectation(exp, exp[memory.ID], slice_expectations, total_matched_count, less_workload)
                if exp.status == expectation.MATCHED:
                    exp.update({memory.HAPPEN_TIME: exp.matched_time})
                    working_memories.push(exp)
                    # new_working_memories.push(exp)
                    expectations.pop(exp[memory.ID])
                elif exp.status == expectation.EXPIRED:
                    expectations.pop(exp[memory.ID])
            total_matched_counts.push(total_matched_count)

        if len(slice_expectations) > 0:
            vision.watch(slice_expectations)
            sound.listen(slice_expectations)

        memory.compose(working_memories)

        

        memory.associate(working_memories, expectations)

        # if watch result is the same for xxx, trigger a random move, 1/16 d, 0.1-0.5 s
        vision.move()
        # all end
        duration = util.time_diff(start)
        fifo_list_durations2s.push(duration)
        fifo_list_durations15s.push(duration)
        fifo_list_durations60s.push(duration)

except KeyboardInterrupt:
    print("quiting...")
    db.housekeep()
