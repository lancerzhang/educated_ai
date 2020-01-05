from components import constants
import collections
import logging
import numpy as np
import pandas as pd
import time

logger = logging.getLogger('dashboard')
logger.setLevel(logging.DEBUG)

LOG_TYPE_LIVE_TIME = False


def log(memories, label):
    data = []
    for x in memories:
        m = [x.memory_type, x.feature_type, x.recall_count, int((time.time() - x.created_time) / 60)]
        data.append(m)
    data = np.array(data)
    field_type = 'type'
    field_feature = 'feature'
    field_recall = 'recall'
    field_live_time = 'liveTime'
    df = pd.DataFrame(data, columns=[field_type, field_feature, field_recall, field_live_time])
    table = df.pivot_table(index=field_recall, columns=field_type, values=field_feature, aggfunc='count',
                           fill_value=0)
    logger.debug(f'{label} count is: {len(memories)}, count by  {field_type}:\n{table}')
    if LOG_TYPE_LIVE_TIME:
        table = df.pivot_table(index=field_live_time, columns=field_type, values=field_feature, aggfunc='count',
                               fill_value=0)
        logger.debug(f'{label} count is: {len(memories)}, count by {field_type}:\n{table}')
