import logging
import sys

from src import brain
from src import dashboard
from src.brain import Brain

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

brain.MEMORY_FILE = '../data/memory.npy'
brain1 = Brain()
brain1.load()
memories = brain1.all_memories
# memories = {x for x in memories if x.status is not MemoryStatus.DORMANT}
# memories = [x for x in memories if x.memory_type == 0 and x.real_type == 3]
# print(len(memories))
# for m in memories:
#     if len(m.parent) == 171:
#         print(m.simple_str())
#         dashboard.log(m.parent, 'parent')
#         dashboard.log(m.children, 'children')
#         f = open('parent.txt', 'w')
#         for x in m.parent:
#             f.write(str(x))

# parent = set()
# for x in memories:
#         if x.mid == 288051305350406992021860502037144657801:
#             print(x.simple_str())
#             x.render_tree(set())
#         print('end')
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
