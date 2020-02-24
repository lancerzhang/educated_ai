import numpy as np
import collections
import json
import time
import logging
import sys
from components import brain
from components import dashboard
from anytree import RenderTree
from components.memory import MemoryStatus
from components.brain import Brain

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

brain.MEMORY_FILE = '../data/memory.npy'
brain1 = Brain()
brain1.load()
memories = brain1.memories
# memories = {x for x in memories if x.status is not MemoryStatus.DORMANT}
# memories = [x for x in memories if x.memory_type == 0]
# print(len(memories))
# for m in memories:
#     if len(m.parent) == 171:
#         print(m)
#         dashboard.log(m.parent, 'parent')
#         dashboard.log(m.children, 'children')
#         f = open('parent.txt', 'w')
#         for x in m.parent:
#             f.write(str(x))

# parent = set()
# for x in memories:
#     if x.memory_type ==0:
#         # if x.mid == 3064:
#         print(x)
#         # x.render_tree(set())
#         for p in x.parent:
#             parent.add(p)
# for p in parent:
#     if p.recall_count>1:
#         print(p.simple_str())
# p.render_tree(set()))
dashboard.log(memories, 'all_memories')
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
