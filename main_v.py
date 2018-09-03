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

expectation = {'id_time': 123456789, 'status': 'new', 'start_time': 123456789, 'end_time': 123456789, 'memory': {}, 'children':{}, 'parent_ids':[]}  # status - new, matching, matched
expectations = {}

db = Database(TinyDB('TinyDB.json'))
memory.db = db

try:
    print 'wake up.\n'
    while 1:
        start = time.time()

        # loop  expectations, find out slice_expectations
        for expectation in expectations:
			expect(expectation);


        # if match some, then if match count is large than x, find more detail,
        vision.watch(slice_expectations)
        sound.hear(slice_expectations)


        # see which memories are met, strength met memories, remove them from expectation,
        # if expire, remove them from expectation,
        #  if nothing match, save and create a new instant/short memory
        # 1st group last 0.5s memories as instant memory
        #  for 0.5-5s, group 4 instant memories as short memory, max 4, more than 4 will be dropped
        #  before 5s, group nearby short memories , max 4, more than 4 will be dropped
        for exp in slice_expectations:
			if exp.status == 'matching':
				do something
			elif exp.status == 'new':
				do something # not matching any, will create a new instant

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
