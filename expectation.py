import time, memory, util

db = None

STATUS = "sts"
NEW = "new"
MATCHING = "mcg"
MATCHED = "mcd"
EXPIRED = "xpd"

START_TIME = "stt"
END_TIME = "edt"

MEMORY = "mmy"
PARENT_ID = "pid"
CHILDREN = "clr"

SLICE_VARIANCE = 0.05

BASIC_EXPECTATION = {STATUS: NEW, START_TIME: 0, END_TIME: 0, CHILDREN: {}}


# check expectation status after sensor processing
# populate slice expectation, for sensor to match
def expect(expectation, slice_expectations, total_matched_count):
    if expectation[memory.TYPE] is not memory.COLLECTION:
        return expectation[STATUS]

    if expectation[STATUS] == NEW:
        if memory.INSTANT_MEMORY == expectation[memory.TYPE_COLLECTION]:
            children_memory_ids = expectation.CHILD_MEM
            interval = 0
            variance = 0.5
            forgot_children = []
            for child_id in children_memory_ids:
                mem = db.get_memory(child_id)
                if mem is not None:
                    now = time.time()
                    child_expectation = {STATUS: NEW, START_TIME: now + interval - variance, END_TIME: now + interval + variance + 0.1, CHILDREN: {}}
                    expectation[CHILDREN].push(expectation.doc_id, child_expectation)
                    slice_expectations.push(child_expectation)
                else:
                    forgot_children.append(child_id)
                    print "forgot"
                interval = interval + 0.1
            if len(forgot_children) > 0:
                memory.remove_memory_children(children_memory_ids, forgot_children, expectation.doc_id)
        elif memory.SLICE_MEMORY == expectation[memory.TYPE_COLLECTION]:
            children_memory_ids = expectation.CHILD_MEM
            forgot_children = []
            for child_id in children_memory_ids:
                mem = db.get_memory(child_id)
                if mem is not None:
                    child_expectation = {STATUS: MATCHING, START_TIME: expectation[START_TIME], END_TIME: expectation[END_TIME]}
                    expectation[CHILDREN].push(expectation.doc_id, child_expectation)
                    slice_expectations.push(child_expectation)
                else:
                    forgot_children.append(child_id)
                    print "forgot"
            if len(forgot_children) > 0:
                memory.remove_memory_children(children_memory_ids, forgot_children, expectation.doc_id)
        else:
            children_memory_ids = expectation.CHILD_MEM
            next_child_id = children_memory_ids[0]
            mem = db.get_memory(next_child_id)
            if mem:
                now = time.time()
                child_expectation = mem.update(
                    {'id_time': time.time(), 'status': NEW, START_TIME: now, END_TIME: now + 0.15, 'memory': {}, 'children': {}})
                expectation.children.push(child_expectation)
                slice_expectations.push(child_expectation)  # if slice not exist, optional to match
            else:
                print "forgot"
        expectation[STATUS] == MATCHING
    elif expectation[STATUS] == MATCHING:
        matched_count = 0
        is_all_matched = True
        is_first_child = True
        children = expectation.children
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
        if matched_count == expectation.CHILD_MEM.count:
            expectation[STATUS] = MATCHED
            expectation.update({'matched_time': time.time()})
            db.use_memory(expectation.doc_id)
        else:
            # all expectation in the queue are matched, but number is not the count of children
            if is_all_matched and (memory.SHORT_MEMORY == expectation[memory.TYPE_COLLECTION] or memory.LONG_MEMORY == expectation[memory.TYPE_COLLECTION]):
                children_memory_ids = expectation.CHILD_MEM
                count = matched_count
                mem = None
                # find next valid memory
                while mem is None and count < children_memory_ids.count:
                    next_child_id = children_memory_ids[count]
                    mem = db.get_memory(next_child_id)
                    count = count + 1
                if mem:
                    now = time.time()
                    child_expectation = mem.update(
                        {'id_time': time.time(), 'status': NEW, START_TIME: now, END_TIME: now + 0.15, 'memory': {}, 'children': {}})
                    expectation.children.push(child_expectation)
                    slice_expectations.push(child_expectation)  # if slice not exist, optional to match
                else:
                    print "forgot"

    return expectation[STATUS]
