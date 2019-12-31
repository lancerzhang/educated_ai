from components import constants
import collections
import logging
import pandas as pd

logger = logging.getLogger('dashboard')
logger.setLevel(logging.INFO)

MIN_RECALL_COUNT = 0


def log(memories, label):
    data = []
    for x in memories:
        m = [x.memory_type, x.feature_type, x.recall_count]
        data.append(m)
    field_memory = 'memory'
    field_feature = 'feature'
    field_recall = 'recall'
    df = pd.DataFrame(data, columns=[field_memory, field_feature, field_recall])
    t1 = df.pivot_table(columns=field_recall, index=field_memory, aggfunc='count', fill_value=0)
    logger.debug(f'{label} {field_memory} count is: {len(memories)}, detail:{t1}')
    t2 = df.pivot_table(columns=field_recall, index=field_feature, aggfunc='count', fill_value=0)
    logger.debug(f'{label} {field_feature} count is: {len(memories)}, detail: {t2}')
