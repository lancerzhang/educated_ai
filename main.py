import time, util, memory, sound, thread, collections
from db import Database
from tinydb import TinyDB, Query

# number of process per second
PPS = 2
# duration per process (s)
DPS = 1.0 / PPS
# limit the time of finding experience memories
FIND_EXP_MEM_TIME = DPS * 0.2
# limit the time of verify experience memories
VERIFY_EXP_MEM_TIME = DPS * 0.3

# expect working memories will match experience memories, if not, working memories will became new experience.
experience_memory = 0
# working memories are reflection of the environment, can find out state from few working memories
working_memory = collections.deque()
working_memory_sound = collections.deque()

db = Database(TinyDB('TinyDB.json'))
sound.db = db
memory.db = db
thread.start_new_thread(sound.listen, ())

try:
    print 'wake up.\n'
    while 1:
        start = time.time()
        # find out the experience start
        related_memory_ids = memory.find_related_memory_ids(working_memory_sound)
        exp_memory_id = memory.find_reward_target(related_memory_ids)
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
        sound.impress(working_memory_sound)
        # all end
        duration = util.time_diff(start)
        # print("All:", duration)
        if duration < DPS:
            # print("Sleep (ms):", (DPS - duration) * 1000)
            time.sleep(DPS - duration)

except KeyboardInterrupt:
    print("quiting...")
    sound.start_thread = False
    db.housekeep()
