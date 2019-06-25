import time
import msvcrt
from components import util

# number of process per second
pps = 10

# duration per process (ms)
dps = 1.0 / pps

testLoop = 2

consume1 = 1000 * 100
consume2 = 1000 * 100

while testLoop > 0:
    if msvcrt.kbhit() and msvcrt.getch() == chr(27).encode():
        print("quiting...")
        break
    start = time.time()
    # do something start 1
    while consume1 > 0:
        consume1 = consume1 - 1
    print(("Task1:", util.time_diff(start) * 1000))
    # do something end 1
    if util.time_diff(start) > dps:
        testLoop = testLoop - 1
        continue
    # do something start 2
    while consume2 > 0:
        consume2 = consume2 - 1
    print(("Task2:", util.time_diff(start) * 1000))
    # do something end 2
    if util.time_diff(start) > dps:
        testLoop = testLoop - 1
        continue
    # all end
    duration = util.time_diff(start)
    print(("All:", duration * 1000))
    testLoop = testLoop - 1
    if duration < dps:
        print(("Sleep:", (dps - duration) * 1000))
        time.sleep(dps - duration)
