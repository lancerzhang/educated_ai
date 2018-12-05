import constants, pyautogui, memory, random

LEFT_CLICK = 'lcl'

data = None


def process(working_memories, work_status, sequential_time_memories):
    actor_mouse_memories = [mem for mem in working_memories if
                            mem[constants.MEMORY_DURATION] is constants.SLICE_MEMORY and mem[
                                constants.PHYSICAL_MEMORY_TYPE] is constants.ACTOR_MOUSE]

    match_actor_mouse_memories(actor_mouse_memories)

    if not work_status[constants.BUSY][constants.MEDIUM_DURATION] or not work_status[constants.REWARD]:
        new_slice_memory = explore()
        if new_slice_memory is not None:
            sequential_time_memories[constants.SLICE_MEMORY].append(new_slice_memory)


def match_actor_mouse_memories(memories):
    for mem in memories:
        click_type = mem[constants.CLICK_TYPE]
        if click_type is LEFT_CLICK:
            pyautogui.click()
            mem[constants.STATUS] = constants.MATCHED
            memory.recall_memory(mem)


def left_click():
    click_type = LEFT_CLICK
    pyautogui.click()
    memories = data.search_actor_mouse(click_type)
    if memories is None or len(memories) == 0:
        action = {constants.PHYSICAL_MEMORY_TYPE: constants.ACTOR_MOUSE, constants.CLICK_TYPE: click_type}
        action_memory = data.add_memory(action)
    else:
        mem = memories[0]
        memory.recall_memory(mem)
        action_memory = mem
    return action_memory


def explore():
    action_memory = left_click()
    slice_memory = None
    if action_memory is not None:
        slice_memory = memory.add_slice_memory([action_memory])
    return slice_memory
