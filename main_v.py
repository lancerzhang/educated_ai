import time, util, memory, collections, vision
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
working_short_memory = np.zeros((3, 50))  # last 0.5 - 5s
working_long_memory = np.zeros(1000)  # before 5s
potential_instant_current = -1
potential_instant_memories = np.zeros(1000)
best_instant_current = -1
best_instant_memory = np.zeros(5)
potential_short_current = -1
potential_short_memories = np.zeros(5)
best_short_current = -1
best_short_memory = np.zeros(5)
best_goal_memory = -1

recent_memory_current = -1
recent_memory = np.zeros((3, 1000))

db = Database(TinyDB('TinyDB.json'))
memory.db = db

try:
    print 'wake up.\n'
    matching_instant_memory = False
    while 1:
        start = time.time()

        # refresh all recent memories
        # from right to left,
        # 1st group last 0.5s memories as instant memory
        #  for 0.5-5s, group 4 instant memories as short memory, max 4, more than 4 will be dropped
        #  before 5s, group nearby short memories , max 4, more than 4 will be dropped

        # find out the experience start, blank start
        if recent_memory_current < 0:
            # find common parents,
            vision.watch()
            related_goal_memory_ids = 0
            possibility = 100 - related_memory_ids
            if possibility < 1:
                vision.watch()
            elif possibility == 99:
                vision.watch()
            else:
                exp_memory_id = memory.find_reward_target(related_memory_ids)
        else:
            if recent_memory_current > 4:
                # combine recent 4 memories to one, if match an exp memory, replace it, or create a new one
                vision.watch()
            else:
                vision.watch()
            vision.watch()

        if matching_instant_memory:
            matching_instant_memory = True

            # find top reward, if more than one, random select one, find goal sequence memory,
            # keep find parent memory, until find top goal, record the goal, record current memory
            # then keep match the memory
            related_memory_ids = memory.find_related_memory_ids(working_instant_memory_vision)
            exp_memory_id = memory.find_reward_target(related_memory_ids)
        else:
            True
            # match memory, if current slice not full match, continue match it,
            # if current slice full match, find next sequence memory
            # if match some, then if match count is large than x, find more detail,
            # if can't match, plus other sequence memory, recalculate goal memory,new_goal = True,
            # if full match, new_goal = True

        # find out the experience start
        # print("find out the experience - used(ms):", util.time_diff(start))
        # find out the experience end
        if util.time_diff(start) > DPS:
            continue
        # find out the best action start
        # print("find out the best action - used(ms):", util.time_diff(start))
        # find out the best action end
        if util.time_diff(start) > DPS:
            continue
        # impress
        vision.watch(memory)
        # compare watch result from different duration, 0.1, 0.2, 0.3, 1, 2, 3, 5
        # compare working & hist memory
        # match short memory 0.5s
        # match middle memory 9s (max 4 elements)
        # match long memory all (max 4 elements)
        # it the same, strength it and find more detail
        # if not, save a new one

        # if watch result is the same for xxx, trigger a random move, 1/16 d, 0.1-0.5 s
        vision.move()
        # all end
        duration = util.time_diff(start)
        # print("All:", duration)
        if duration < DPS:
            # print("Sleep (ms):", (DPS - duration) * 1000)
            time.sleep(DPS - duration)

except KeyboardInterrupt:
    print("quiting...")
    db.housekeep()
