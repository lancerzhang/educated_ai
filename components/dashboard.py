from components import constants
import collections
import logging
import numpy as np
import pandas as pd
import time

logger = logging.getLogger('dashboard')
logger.setLevel(logging.DEBUG)

LOG_TYPE_LIVE_TIME = False
LOG_TYPE_ACTIVE_TIME = True


def log(memories, label, need_active=False):
    data = []
    for x in memories:
        if x.live and x.status in [constants.MATCHING, constants.MATCHED] and x.active_end_time:
            active_time = x.get_active_time()
        else:
            active_time = 0
        m = [x.memory_type, x.feature_type, x.recall_count, x.status, int((time.time() - x.created_time) / 60),
             int(active_time)]
        data.append(m)
    data = np.array(data)
    field_type = 'type'
    field_feature = 'feature'
    field_recall = 'recall'
    field_status = 'status'
    field_live_time = 'liveTime'
    field_active_time = 'active_time'
    df = pd.DataFrame(data, columns=[field_type, field_feature, field_recall, field_status, field_live_time,
                                     field_active_time])
    table = df.pivot_table(index=[field_recall], columns=[field_status, field_type], values=field_feature,
                           aggfunc='count', fill_value=0)
    logger.debug(f'{label} count is: {len(memories)}, count by  {field_type}:\n{table.to_string()}')
    if LOG_TYPE_LIVE_TIME:
        table = df.pivot_table(index=field_live_time, columns=field_type, values=field_feature, aggfunc='count',
                               fill_value=0)
        logger.debug(f'{label} count is: {len(memories)}, count by {field_type}:\n{table.to_string()}')
    if need_active:
        table = df.pivot_table(index=field_active_time, columns=field_type, values=field_feature, aggfunc='count',
                               fill_value=0)
        logger.debug(f'{label} count is: {len(memories)}, count by {field_type}:\n{table.to_string()}')
