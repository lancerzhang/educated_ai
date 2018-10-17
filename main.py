import time, util, memory, collections, vision, expectation, sound, copy
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

workloads = {}

frames = 0
db = Database(TinyDB('TinyDB.json'))
memory.db = db


def init_workloads():
    if len(workloads) == 0:
        # if free in short time, find more detail, explore the world
        short_duration = [0] * 2 * PPS
        # if free in middle time, try different flow, see which one is better (with higher reward)
        middle_duration = [0] * 15 * PPS
        # if free in long time, clean up memories
        long_duration = [0] * 60 * PPS
        workloads.update({'duration': {'S': short_duration}})
        workloads.update({'duration': {'M': middle_duration}})
        workloads.update({'duration': {'L': long_duration}})
        workloads.update({'busy': {'S': False}})
        workloads.update({'busy': {'M': False}})
        workloads.update({'busy': {'L': False}})


def calculate_workload(frames, flag):
    if frames > len(workloads['duration'][flag]) and util.avg(workloads['duration'][flag]) > DPS:
        workloads.update({'busy': {flag: True}})
    else:
        workloads.update({'busy': {flag: False}})


def calculate_workloads(frames):
    calculate_workload(frames, 'S')
    calculate_workload(frames, 'M')
    calculate_workload(frames, 'L')


def update_workloads(duration):
    workloads['duration']['S'].push(duration)
    workloads['duration']['M'].push(duration)
    workloads['duration']['L'].push(duration)


try:
    print 'wake up.\n'
    sequential_time_memories = copy.deepcopy(memory.BASIC_MEMORY_GROUP_ARR)
    while 1:
        frames = frames + 1
        start = time.time()

        calculate_workloads(frames)

        if len(working_memories) == 0:
            vision.watch()
            sound.listen()
        else:
            memory.associate(working_memories)
            memory.prepare_expectation(working_memories)
            vision.watch(working_memories)
            sound.hear(working_memories)
            memory.check_expectation(working_memories)
            memory.compose(sequential_time_memories)

        if len(working_memories) > 0:
            vision.watch(working_memories)
            sound.listen(working_memories)

        memory.compose(sequential_time_memories)

        memory.associate(sequential_time_memories, working_memories)

        # if watch result is the same for xxx, trigger a random move, 1/16 d, 0.1-0.5 s
        vision.move()
        # all end
        duration = util.time_diff(start)
        update_workloads(duration)

        if workloads['busy']['M']:
            working_memories = memory.cleanup_working_memories(working_memories)

except KeyboardInterrupt:
    print("quiting...")
    db.housekeep()
