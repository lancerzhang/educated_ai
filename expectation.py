import time, memory, util

db = None

ID_TIME = 'idt'
STATUS = 'sts'
NEW = 'new'
MATCHING = 'mcg'
MATCHED = 'mcd'
EXPIRED = 'xpd'

START_TIME = 'stt'
END_TIME = 'edt'

MEMORY = 'mmy'
PARENT_ID = 'pid'
CHILDREN = 'clr'

SLICE_VARIANCE = 0.05

BASIC_EXPECTATION = {STATUS: NEW, START_TIME: 0, END_TIME: 0, CHILDREN: {}}


# check expectation status after sensor processing
# populate slice expectation, for sensor to match
def expect(expectation, slice_expectations, total_matched_count):
    if expectation[memory.TYPE] is not memory.COLLECTION:
        return expectation[STATUS]

    if expectation[STATUS] == NEW:
        if memory.INSTANT_MEMORY == expectation[memory.TYPE_COLLECTION]:
            children = memory.get_valid_child_memory(expectation)
            interval = 0
            variance = 0.5
            now = time.time()
            for child in children:
                child.update({ID_TIME: time.time(), STATUS: NEW, START_TIME: now + interval - variance, END_TIME: now + interval + variance + 0.1, CHILDREN: {}})
                expectation[CHILDREN].push(child[memory.ID], child)
                slice_expectations.push(child)
                interval = interval + 0.1
        elif memory.SLICE_MEMORY == expectation[memory.TYPE_COLLECTION]:
            children = memory.get_valid_child_memory(expectation)
            for child in children:
                child.update({ID_TIME: time.time(), STATUS: MATCHING, START_TIME: expectation[START_TIME], END_TIME: expectation[END_TIME], CHILDREN: {}})
                expectation[CHILDREN].push(child[memory.ID], child)
                slice_expectations.push(child)
        else:
            # for short or long memory, only get next new child
            children = memory.get_valid_child_memory(expectation, 1)
            for child in children:
                child.update({ID_TIME: time.time(), STATUS: MATCHING, START_TIME: expectation[START_TIME], END_TIME: expectation[END_TIME], CHILDREN: {}})
                expectation[CHILDREN].push(child[memory.ID], child)
                slice_expectations.push(child)
        expectation[STATUS] == MATCHING
    elif expectation[STATUS] == MATCHING:
        matched_count = 0
        is_all_matched = True
        is_first_child = True
        children = expectation[CHILDREN]
        for child in children:
            status = expect(child, expectation, total_matched_count)
            if status == MATCHED:
                matched_count = matched_count + 1
                total_matched_count = total_matched_count + 1
            elif status == EXPIRED:
                if memory.LONG_MEMORY == expectation[memory.TYPE_COLLECTION]:
                    if is_first_child:
                        expectation[STATUS] = EXPIRED
                    else:
                        expectation.child[STATUS] = NEW
                else:
                    expectation[STATUS] = EXPIRED
            else:
                is_all_matched = False
            is_first_child = False
        if matched_count == expectation[memory.CHILD_MEM].count:
            expectation[STATUS] = MATCHED
            expectation.update({'matched_time': time.time()})
        else:
            # all expectation in the queue are matched, but number is not the count of children
            if is_all_matched and (memory.SHORT_MEMORY == expectation[memory.TYPE_COLLECTION] or memory.LONG_MEMORY == expectation[memory.TYPE_COLLECTION]):
                children_memory_ids = expectation[memory.CHILD_MEM]
                children = memory.get_valid_child_memory(expectation, 1, matched_count)
                for child in children:
                    now = time.time()
                    child_expectation = child.update(
                        {ID_TIME: time.time(), STATUS: NEW, START_TIME: now, END_TIME: now + 0.15, CHILDREN: {}})
                    expectation.children.push(child_expectation)
                    slice_expectations.push(child_expectation)  # if slice not exist, optional to match

    return expectation[STATUS]
