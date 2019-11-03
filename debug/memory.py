import numpy as np
import time
from components import memory
from components.memory import Memory
from components.brain import Brain

memories = set(np.load('../data/memory.npy', allow_pickle=True))
print(len(memories))

b = Brain()
b.memories = memories
q = Memory()
q.memory_type = 1
q.feature_type = 1
t1 = time.time()
m = b.find_memory(q)
t2 = time.time()
print((t2 - t1) * 1000)
