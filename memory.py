import time, random

# use parent to find experience memories
basic_memory = {'strength': 0, 'recall': 0, 'reward': 0, 'lastRecall': 0, 'parents': []}

# The first recall time, if less than 60 seconds, memory strength is 100%, and then 99% for 61 seconds ... 21% for 35 days
time_sec = [60, 61, 63, 66, 70, 75, 81, 88, 96, 105, 115, 126, 138, 151, 165, 180, 196, 213, 231, 250, 270, 291, 313, 336, 360, 385, 411, 438, 466, 495, 525, 540, 600, 660, 720,
            780, 840, 900, 960, 1020, 1080, 1140, 1200, 1260, 1320, 1440, 1560, 1740, 1920, 2100, 2280, 2460, 2640, 2880, 3120, 3360, 3600, 4680, 6120, 7920, 10440, 14040, 18720,
            24840, 32400, 41760, 52920, 66240, 81720, 99720, 120240, 143640, 169920, 222480, 327600, 537840, 853200, 1326240, 2035800, 3100140,
            3609835, 4203316, 4894372, 5699043, 6636009, 7727020, 8997403, 10476649, 12199095, 14204727, 16540102, 19259434, 22425848, 26112847, 30406022, 35405033, 41225925,
            48003823, 55896067, 65085866]

forget_memory = False


# longer time elapsed, easier to forget
# more times recall, harder to forget
# can not recall frequently in short time
def refresh(mem, recall=False):
    time_elapse = time.time() - mem['lastRecall']
    if time_elapse < 60:
        return
    count = 0
    for num in range(mem['recall'], len(time_sec)):
        if time_sec[num] <= time_elapse:
            count = count + 1
        else:
            strength = 100 - count
            mem['strength'] = strength
            if count > 0:
                # random forget memory base on strength
                if forget_memory:
                    ran = random.randint(1, 100)
                    if ran > strength:
                        mem['strength'] = -1
                        break
                # if this is recall, will update recall count and last recall time
                if recall:
                    mem['recall'] = mem['recall'] + 1
                    mem['lastRecall'] = time.time()
            break


# TODO, need to check if parent memory is valid or not
# summarize all parent memories in a list
def find_parents(working_memories):
    parent_counts = {}
    for mem in working_memories:
        parents = mem['parents']
        for parent in parents:
            pc = parent_counts.get(parent)
            if pc:
                parent_counts.update({parent: pc + 1})
            else:
                parent_counts.update({parent: 1})
    return parent_counts


# find out max occurrence in parent memories of all working memories
# if all occur once, return [] (not found)
def find_related_memory_ids(working_memories):
    parent_counts = find_parents(working_memories)
    max_value = 0
    max_ids = []
    max_count = 0
    for key, value in parent_counts.items():
        if value > max_count:
            max_value = value
            max_count = max_count + 1
    if max_count == 1:
        max_ids = []
    else:
        for key, value in parent_counts.items():
            if value == max_value:
                max_ids.append(key)
    return max_ids


# find max reward in memories (db record)
def find_exp_memory(related_memories):
    max_value = 0
    max_id = 0
    for mem in related_memories:
        reward = mem['reward']
        if reward > max_value:
            max_value = reward
            max_id = mem.doc_id
    return max_id
