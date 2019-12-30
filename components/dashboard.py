from components import constants
import collections
import logging

logger = logging.getLogger('dashboard')
logger.setLevel(logging.DEBUG)

MIN_RECALL_COUNT = 1


def log(memories, label):
    memories = [x for x in memories if x[constants.RECALL_COUNT] > MIN_RECALL_COUNT]
    logger.debug(f'{label} number of memories that recall greater than {MIN_RECALL_COUNT} is {len(memories)}')

    memory_types = [x[constants.VIRTUAL_MEMORY_TYPE] for x in memories if constants.VIRTUAL_MEMORY_TYPE in x]
    memory_types_counter = collections.Counter(memory_types)
    logger.debug(f'{label} VIRTUAL_MEMORY_TYPE counter:{sorted(memory_types_counter.items())}')

    feature_type = [x[constants.PHYSICAL_MEMORY_TYPE] for x in memories if constants.PHYSICAL_MEMORY_TYPE in x]
    feature_type_counter = collections.Counter(feature_type)
    logger.debug(f'{label} feature_type_counter:{sorted(feature_type_counter.items())}')

    recall_count = [x[constants.RECALL_COUNT] for x in memories]
    recall_count_counter = collections.Counter(recall_count)
    logger.debug(f'{label} recall_count_counter:{sorted(recall_count_counter.items())}')

    recall_count = [x[constants.RECALL_COUNT] for x in memories]
    recall_count_counter = collections.Counter(recall_count)
    logger.debug(f'{label} recall_count_counter:{sorted(recall_count_counter.items())}')
