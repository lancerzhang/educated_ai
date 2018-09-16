import time, memory, util

db = None

NEW="new"
MATCHING="matching"
MATCHED="matched"
EXPIRED="expired"

START_TIME="start_time"
END_TIME="end_time"


#check expectation status after sensor processing
#populate slice expectation, for sensor to match
def expect(expectation, parent_id,slice_expectations,total_matched_count,less_workload):
    if expectation.memory[memory.TYPE] is not memory.COLLECTION:
        return expectation.status
		
	if expectation.status == NEW:
		if memory.INSTANT_MEMORY == expectation.memory[memory.TYPE_COLLECTION]:
			children_memory_ids =expectation.memory.CHILD_DATA
			interval=0
			varience=0.5
			for child_id in children_memory_ids:
				mem =db.get_memory(child_id)
				if mem:
					now = time.time()
					sub_expectation =mem.update({'id_time': now, 'status': NEW, START_TIME: now+interval-varience, END_TIME: now+interval+varience+0.1, 'memory': {} ,'parent_id':parent_id,'children':{}})
					expectation.children.push(sub_expectation)
					slice_expectations.push(sub_expectation)
				else:
					print "forgot"
				interval=interval+0.1
		elif memory.SLICE_MEMORY == expectation.memory[memory.TYPE_COLLECTION]:
			children_memory_ids =expectation.memory.CHILD_DATA
			for child_id in children_memory_ids:
				mem =db.get_memory(child_id)
				if mem:
					now = time.time()
					sub_expectation =mem.update({'id_time': now, 'status': MATCHING, START_TIME: expectation[START_TIME], END_TIME: expectation[END_TIME], 'memory': {} ,'parent_id':parent_id})
					expectation.children.push(sub_expectation)
					slice_expectations.push(sub_expectation)
				else:
					print "forgot"
		else:
			children_memory_ids =expectation.memory.CHILD_DATA
			first_child_id=children_memory_ids[0]
			mem =db.get_memory(first_child_id)
			if mem:
				now = time.time()
				sub_expectation =mem.update({'id_time': time.time(), 'status': NEW, START_TIME: now, END_TIME: now+0.15, 'memory': {} ,'parent_id':parent_id,'children':{}})
				expectation.children.push(sub_expectation)
				slice_expectations.push(sub_expectation)  # if slice not exist, optional to match
			else:
				print "forgot"
		expectation.status == MATCHING
	elif expectation.status == MATCHING:
		expired=False
		matched_count=0
		is_all_matched=True
		is_first_child=True
		children =expectation.children
		for child in children:
			status=expect(child)
			if status==MATCHED:
				matched_count=matched_count+1
				total_matched_count=total_matched_count+1
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
			else:
				is_all_matched=False
			is_first_child=False
		if matched_count==expectation.memory.CHILD_DATA.count:
			expectation.status=MATCHED
			expectation.update({'matched_time':time.time()})
			db.use_memory(expectation.memory.elid)
		else:
			#all expectation in the queue are matched, but number is not the count of children
			if is_all_matched and (memory.SHORT_MEMORY == expectation.memory[memory.TYPE_COLLECTION] or memory.LONG_MEMORY == expectation.memory[memory.TYPE_COLLECTION]):
				children_memory_ids =expectation.memory.CHILD_DATA
				count=matched_count
				mem =None
				while mem is None and count<children_memory_ids.count:
					children_memory_ids[count]
					mem=db.get_memory(first_child_id)
				if mem:
					now = time.time()
					sub_expectation =mem.update({'id_time': time.time(), 'status': NEW, START_TIME: now, END_TIME: now+0.15, 'memory': {} ,'parent_id':parent_id,'children':{}})
					expectation.children.push(sub_expectation)
					slice_expectations.push(sub_expectation)  # if slice not exist, optional to match
				else:
					print "forgot"
	
    return expectation.status
