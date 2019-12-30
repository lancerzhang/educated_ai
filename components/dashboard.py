from components import constants
import collections
import logging

logger = logging.getLogger('dashboard')
logger.setLevel(logging.DEBUG)

MIN_RECALL_COUNT = 0


def log(memories, label):
    memories = [x for x in memories if x[constants.RECALL_COUNT] > MIN_RECALL_COUNT]
    logger.debug(f'{label} number of memories that recall greater than {MIN_RECALL_COUNT} is {len(memories)}')

    memory_types = [x[constants.VIRTUAL_MEMORY_TYPE] for x in memories if constants.VIRTUAL_MEMORY_TYPE in x]
    memory_types_counter = collections.Counter(memory_types)
    logger.debug(f'{label} memory_types counter:{sorted(memory_types_counter.items())}')

    feature_type = [x[constants.PHYSICAL_MEMORY_TYPE] for x in memories if constants.PHYSICAL_MEMORY_TYPE in x]
    feature_type_counter = collections.Counter(feature_type)
    logger.debug(f'{label} feature_type counter:{sorted(feature_type_counter.items())}')

    recall_count = [x[constants.RECALL_COUNT] for x in memories]
    recall_count_counter = collections.Counter(recall_count)
    logger.debug(f'{label} recall_count counter:{sorted(recall_count_counter.items())}')

    children_len_count = [len(x[constants.CHILD_MEM]) for x in memories]
    children_len_count_counter = collections.Counter(children_len_count)
    logger.debug(f'{label} children_len counter:{sorted(children_len_count_counter.items())}')
