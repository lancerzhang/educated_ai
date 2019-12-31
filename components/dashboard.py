from components import constants
import logging
import pandas as pd

logger = logging.getLogger('dashboard')
logger.setLevel(logging.INFO)


def log(memories, label):
    data = []
    for x in memories:
        if constants.VIRTUAL_MEMORY_TYPE in x:
            memory_type = x[constants.VIRTUAL_MEMORY_TYPE]
        else:
            memory_type = 0
        if constants.PHYSICAL_MEMORY_TYPE in x:
            feature_type = x[constants.PHYSICAL_MEMORY_TYPE]
        else:
            feature_type = 0
        m = [memory_type, feature_type, x[constants.RECALL_COUNT]]
        data.append(m)
    field_memory = 'memory'
    field_feature = 'feature'
    field_recall = 'recall'
    df = pd.DataFrame(data, columns=[field_memory, field_feature, field_recall])
    t1 = df.pivot_table(columns=field_recall, index=field_memory, aggfunc='count', fill_value=0)
    logger.debug(f'{label} {field_memory} count is: {len(memories)}, detail:{t1}')
    t2 = df.pivot_table(columns=field_recall, index=field_feature, aggfunc='count', fill_value=0)
    logger.debug(f'{label} {field_feature} count is: {len(memories)}, detail:{t2}')
