import time, memory, util

db = None

NEW="new"
MATCHING="matching"
MATCHED="matched"
EXPIRED="expired"
FORGOT="forgot"
START_TIME="start_time"
END_TIME="end_time"

#populate slice expectation, for sensor to match
def expect_start(expectation, parent_id,slice_expectations):
    if expectation.memory[memory.TYPE] is not memory.COLLECTION:
        return "incorrect type of memory"

    now = time.time()
    if (expectation[START_TIME] > 0 and expectation[START_TIME] - now > 0) or (expectation[END_TIME] > 0 and now - expectation[END_TIME]) > 0:
        return "not in time"

	if memory.SLICE_MEMORY == expectation.memory[memory.TYPE_COLLECTION]:
		return "end of searching"
		
	if expectation.status == MATCHED or expectation.status == EXPIRED:
		return expectation.status
	
	if expectation.status == NEW:
		if memory.INSTANT_MEMORY == expectation.memory[memory.TYPE_COLLECTION]:
			children_memory_ids =expectation.memory.CHILD_DATA
			interval=0
			varience=0.5
			for child_id in children_memory_ids:
				mem =db.get_memory(child_id)
				now = time.time()
				sub_expectation =mem.update({'id_time': time.time(), 'status': NEW, START_TIME: now+interval-varience, END_TIME: now+interval+varience+0.1, 'memory': {} ,'parent_id':parent_id,'children':{}})
				expectation.children.push(sub_expectation)
				slice_expectations.push(sub_expectation)  # if slice not exist, optional to match
				interval=interval+0.1
		elif:
			children_memory_ids =expectation.memory.CHILD_DATA
			first_child_id=children_memory_ids[0]
			mem =db.get_memory(first_child_id)
			now = time.time()
			sub_expectation =mem.update({'id_time': time.time(), 'status': NEW, START_TIME: now, END_TIME: now+0.15, 'memory': {} ,'parent_id':parent_id,'children':{}})
			expectation.children.push(sub_expectation)
			slice_expectations.push(sub_expectation)  # if slice not exist, optional to match
		expectation.status == MATCHING
	elif expectation.status == MATCHING:
		if memory.INSTANT_MEMORY != expectation.memory[memory.TYPE_COLLECTION]:
			for child in expectation.children:

				
	for child in expectation.children:
		find_next=False
		if child.status ==MATCHED:
			find_next=True
		elif child.status ==MATCHING:
			find_next=False


#check expectation status after sensor processing
def expect_end(expectation):
	children =expectation.children
	if !children:
		if expectation.end_time > 0 and now - expectation.end_time > 0:
			expectation.status=EXPIRED
		return expectation.status
	
	all_match=True
	expired=False
	is_first_child=True
	for child in children:
		status=expect_end(child)
		if status!=MATCHED:
			all_match=False
		elif status==EXPIRED:
			expired=True
			if memory.LONG_MEMORY == expectation.memory[memory.TYPE_COLLECTION]:
				if is_first_child:
					expectation.status=EXPIRED
				elif:
					expectation.child.status=NEW
			elif:
				expectation.status=EXPIRED
			break
		is_first_child=False
	if all_match:
		expectation.status=MATCHED
		db.use_memory(expectation.memory.elid)
	
	return expectation.status
	
