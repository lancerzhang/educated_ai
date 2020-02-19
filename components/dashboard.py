from components import constants
from components.memory import MemoryType
from components.memory import MemoryStatus
import collections
import logging
import numpy as np
import pandas as pd
import time

logger = logging.getLogger('dashboard')
logger.setLevel(logging.DEBUG)

LOG_TYPE_LIVE_TIME = True
LOG_TYPE_ACTIVE_TIME = True


def log(memories, label, with_status=False, need_active=False):
    data = []
    for x in memories:
        if x.status in [MemoryStatus.MATCHING, MemoryStatus.MATCHED] and x.active_end_time:
            active_time = x.get_active_time()
        else:
            active_time = 0
        m = [x.memory_type, x.real_type, x.recall_count, x.status, int((time.time() - x.created_time) / 60),
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
    if with_status:
        pt_columns = [field_status, field_type]
    else:
        pt_columns = [field_type]
    table = df.pivot_table(index=[field_recall], columns=pt_columns, values=field_feature,
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
