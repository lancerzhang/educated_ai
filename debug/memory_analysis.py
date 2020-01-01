import numpy as np
import collections
import json
import time
import logging
import sys
from components import constants
from components import dashboard
from components.memory import Memory
from components.brain import Brain

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

brain = Brain()
brain.MEMORY_FILE = '../data/memory.npy'
brain.load()
memories = brain.memories
# for m in memories:
#     if m.feature == constants.VISION_FOCUS_MOVE:
#         print(str(m))
brain.cleanup_memories()
memories = brain.memories
dashboard.MIN_RECALL_COUNT = 2
dashboard.log(memories, 'ALL',True)
# ff = open('features.txt', 'w')
# fs = set()
# for m in features:
#     f = f'{m.kernel}|{m.feature}\n'
#     if f in fs:
#         print(f'duplicated:{f}')
#     fs.add(f)
#     sf.write(s)
#     ff.write(f'{str(m)}\n')
# print(f'len of set is:{len(fs)}')

# virtual = [x for x in memories if x.memory_type > 0]
# print(f'len of virtual is {len(virtual)}')
# vf = open('virtual.txt', 'w')
# vs = set()
# for m in virtual:
#     v = f'{m.children}\n'
#     if v in vs:
#         print(f'duplicated:{v}')
#     vs.add(v)
#     # sf.write(s)
#     vf.write(f'{str(m)}\n')
# print(f'len of set is:{len(vs)}')
