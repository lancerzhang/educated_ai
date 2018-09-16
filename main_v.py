import time, util, memory, collections, vision,expectation
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

working_memories=[]
new_working_memories=[]
total_matched_counts=[0,0,0]
durations=[0,0,0]
db = Database(TinyDB('TinyDB.json'))
memory.db = db

try:
    print 'wake up.\n'
    while 1:
        start = time.time()
		
		less_workload=False
		if avg(durations) <DPS:
			less_workload=True

        if sum(total_matched_counts)==0 or slice_expectations.empyt():
			vision.watch()
			sound.hear()
		else:
			vision.watch(slice_expectations)
			sound.hear(slice_expectations)
			total_matched_count=0
			# loop  expectations, find out slice_expectations
			for exp in expectations:
				expect(exp,expectation.id_time,slice_expectations, total_matched_count,less_workload);
				if exp.status==expectation.MATCHED:
					mem=expectation.memory.copy()
					mem.update({memory.HAPPEN_TIME:exp.matched_time})
					working_memories.push(mem)
					new_working_memories.push(mem)
					expectations.remove(exp)
				elif exp.status==expectation.EXPIRED:
					expectations.remove(exp)
			total_matched_counts.push(total_matched_count)
		
		if expectations.has_slice():
			vision.watch()
			sound.hear()
			
		memory.compose(working_memories,new_working_memories)
        
		mem=memory.associate(working_memories)
		if mem
			expectation.push_memory(mem)

        # if watch result is the same for xxx, trigger a random move, 1/16 d, 0.1-0.5 s
        vision.move()
        # all end
        duration = util.time_diff(start)
		durations.push(duration)

except KeyboardInterrupt:
    print("quiting...")
    db.housekeep()
