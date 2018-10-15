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

# to group them as a new memory by time sequence
sequential_time_memories = {}

# matched memory tree
active_memory_trees = {}

# reference of active_memory_trees, for cleaning up active memory, associate expectation
# not full tree, just limit of number (11? similar to working memory?)
# matched / elder / child memory will be higher priority to clean up
# pending / newer / parent / high reward memory will be lower priority to clean up
# this is most important for making decision (what's next expectation)
# pure memory recall (when free) will impact this, which it is "thinking"
# interruption from environment can impact this, which it is "disturb"
active_memory_arr = []

# to find out slice expectations
# compare to active memory tree, this is not happen
expectation_trees = {}

# array, used by sensor
slice_expectations = []

total_matched_counts = [0, 0, 0]
fifo_list_durations2s = [0] * 2 * PPS
fifo_list_durations15s = [0] * 15 * PPS
fifo_list_durations60s = [0] * 60 * PPS
frames = 0
db = Database(TinyDB('TinyDB.json'))
memory.db = db

try:
    print 'wake up.\n'
    sequential_time_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
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
            for exp in expectation_trees:
                expectation.prepare_expectation(exp, exp[memory.ID], slice_expectations, total_matched_count, less_workload)
                if exp.status == expectation.MATCHED:
                    exp.update({memory.HAPPEN_TIME: exp.matched_time})
                    sequential_time_memories.push(exp)
                    # new_working_memories.push(exp)
                    expectation_trees.pop(exp[memory.ID])
                elif exp.status == expectation.EXPIRED:
                    expectation_trees.pop(exp[memory.ID])
            total_matched_counts.push(total_matched_count)

        if len(slice_expectations) > 0:
            vision.watch(slice_expectations)
            sound.listen(slice_expectations)

        memory.compose(sequential_time_memories)

        memory.associate(sequential_time_memories, expectation_trees)

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
