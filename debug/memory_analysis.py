import numpy as np
import collections
import json
import time
from components import memory
from components.memory import Memory
from components.brain import Brain

memories = set(np.load('../data/memory.npy', allow_pickle=True))
print(len(memories))

brain = Brain()
brain.memories = memories
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

# sounds = [x for x in memories if x.memory_type == 0]
# for m in sounds:
#     print(m)

# for m in memories:
#     for x in memories:
#         if x.mid!=m.mid and x.equal(m):
#             print(f'duplicated:{x.mid} and {m.mid}')
