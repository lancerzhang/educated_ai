import constants, pyautogui, memory, random, time

LEFT_CLICK = 'lcl'

data_service = None
pyautogui.PAUSE = 0.0001


def process(working_memories, sequential_time_memories, work_status):
    actor_mouse_memories = [mem for mem in working_memories if
                            constants.MEMORY_DURATION in mem and
                            mem[constants.MEMORY_DURATION] is constants.SLICE_MEMORY and
                            mem[constants.STATUS] is constants.MATCHING and
                            mem[constants.PHYSICAL_MEMORY_TYPE] is constants.ACTOR_MOUSE]

    matched_feature_memories = match_actor_mouse_memories(actor_mouse_memories)

    for mem in matched_feature_memories:
        working_memories.append(mem)

    if not work_status[constants.BUSY][constants.MEDIUM_DURATION] or not work_status[constants.REWARD]:
        new_slice_memory = explore()
        if new_slice_memory is not None:
            sequential_time_memories[constants.SLICE_MEMORY].append(new_slice_memory)
            working_memories.append(new_slice_memory)


def match_actor_mouse_memories(memories):
    matched_memories = []
    for mem in memories:
        click_type = mem[constants.CLICK_TYPE]
        if click_type is LEFT_CLICK:
            pyautogui.click()
            mem[constants.STATUS] = constants.MATCHED
            memory.recall_memory(mem)
            mem.update({constants.HAPPEN_TIME: time.time()})
            matched_memories.append(mem)
    return matched_memories


def left_click():
    click_type = LEFT_CLICK
    pyautogui.click()
    mem = data_service.get_actor_mouse_memory(click_type)
    if mem is None:
        action = {constants.PHYSICAL_MEMORY_TYPE: constants.ACTOR_MOUSE, constants.CLICK_TYPE: click_type}
        action_memory = memory.add_physical_memory(action)
    else:
        memory.recall_memory(mem)
        action_memory = mem
    return action_memory


def explore():
    start = time.time()
    action_memory = left_click()
    slice_memory = None
    if action_memory is not None:
        slice_memory = memory.add_collection_memory(constants.SLICE_MEMORY, [action_memory])
    # print 'explore	' + str(time.time() - start)
    return slice_memory
