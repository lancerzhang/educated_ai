import time, util, memory
from db import Database
from tinydb import TinyDB, Query

# number of process per second
pps = 10
# duration per process (s)
dps = 1.0 / pps
# limit the time of finding experience memories
find_exp_mem_time = dps * 0.3
# limit the time of verify experience memories
verify_exp_mem_time = dps * 0.3

# expect working memories will match experience memories, if not, working memories will became new experience.
experience_memory = 0
# working memories are reflection of the environment, can find out state from few working memories
working_memory = []

database = Database(TinyDB(TinyDB('TinyDB.json')))

try:
    while 1:
        start = time.time()
        # find out the experience start
        experience_memory = memory.find_exp_memory(working_memory)
        print("find out the experience - used(ms):", util.time_diff(start))
        # find out the experience end
        if util.time_diff(start) > dps:
            continue
        # find out the best action start
        print("find out the best action - used(ms):", util.time_diff(start))
        # find out the best action end
        if util.time_diff(start) > dps:
            continue
        # all end
        duration = util.time_diff(start)
        print("All:", duration)
        if duration < dps:
            print("Sleep:", (dps - duration))
            time.sleep(dps - duration)

except KeyboardInterrupt:
    print("quiting...")
    database.cleanup_memory()
