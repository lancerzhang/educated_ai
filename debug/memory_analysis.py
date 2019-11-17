import numpy as np
import collections
import json
import time
from components import memory
from components.memory import Memory
from components.brain import Brain

brain = Brain()
brain.memory_file = '../data/memory.npy'
brain.load()
memories = brain.memories
print(len(memories))
brain.cleanup_memories()
brain.cleanup_memories()
brain.cleanup_memories()
print(len(brain.memories))
memories = brain.memories

memory_types = [x.memory_type for x in memories]
memory_types_counter = collections.Counter(memory_types)
print(f'memory_types_counter:{memory_types_counter}')

feature_type = [x.feature_type for x in memories]
feature_type_counter = collections.Counter(feature_type)
print(f'feature_type_counter:{feature_type_counter}')

recall_count = [x.recall_count for x in memories]
recall_count_counter = collections.Counter(recall_count)
print(f'recall_count_counter:{recall_count_counter}')

children = [len(x.children) for x in memories if x.memory_type > 0]
children_counter = collections.Counter(children)
print(f'children_counter:{children_counter}')

features = [x for x in memories if x.memory_type == 0 and x.feature_type == 0]
print(f'len of features is {len(features)}')
ff = open('features.txt', 'w')
fs = set()
for m in features:
    f = f'{m.kernel}|{m.feature}\n'
    if f in fs:
        print(f'duplicated:{f}')
    fs.add(f)
    # sf.write(s)
    ff.write(f'{str(m)}\n')
print(f'len of set is:{len(fs)}')

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
