import time, util, memory, collections, vision, expectation, sound
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

working_memories = []
new_working_memories = []
total_matched_counts = [0, 0, 0]
durations = [0, 0, 0]
db = Database(TinyDB('TinyDB.json'))
memory.db = db

try:
    print 'wake up.\n'
    while 1:
        start = time.time()
        less_workload = False
        if util.avg(durations) < DPS:
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
                expectation.expect(exp, exp['doc_id'], slice_expectations, total_matched_count, less_workload);
                if exp.status == expectation.MATCHED:
                    exp.update({memory.HAPPEN_TIME: exp.matched_time})
                    working_memories.push(exp)
                    new_working_memories.push(exp)
                    expectations.pop(exp['doc_id'])
                elif exp.status == expectation.EXPIRED:
                    expectations.pop(exp['doc_id'])
            total_matched_counts.push(total_matched_count)

        if len(slice_expectations) > 0:
            vision.watch(slice_expectations)
            sound.listen(slice_expectations)

        memory.compose(working_memories, new_working_memories)

        memory.associate(new_working_memories, expectations)

        # if watch result is the same for xxx, trigger a random move, 1/16 d, 0.1-0.5 s
        vision.move()
        # all end
        duration = util.time_diff(start)
        durations.push(duration)

except KeyboardInterrupt:
    print("quiting...")
    db.housekeep()
