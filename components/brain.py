from components.memory import Memory
from components import constants
from components import util


class Brain:
    def __init__(self):
        self.memories = set()
        self.active_memories = []
        self.memory_id_sequence = 0

    def associate_active_memories(self):
        active_parent = []
        for mem in self.active_memories:
            active_parent.append(mem.parent)
        parent_counts = util.list_element_count(active_parent)
        for memory in sorted(parent_counts, key=parent_counts.get, reverse=True):
            if memory not in self.active_memories:
                memory.activate()
                self.active_memories.append(memory)
                break

    def prepare_active_memories(self):
        for memory in self.active_memories:
            memory.activate_tree()

    def match_virtual_memories(self):
        for memory in self.active_memories:
            if memory.virtual_type == constants.SLICE_MEMORY:
                memory.match()

        for memory in self.active_memories:
            if memory.virtual_type == constants.INSTANT_MEMORY:
                memory.match()

        for memory in self.active_memories:
            if memory.virtual_type == constants.SHORT_MEMORY:
                memory.match()

        match_any = True
        while match_any:
            match_any = False
            for memory in self.active_memories:
                if memory.virtual_type == constants.LONG_MEMORY:
                    if memory.match():
                        match_any = True

    def compose_memory(self, virtual_type, active_memories):
        if len(active_memories) == 0:
            return
        memories = active_memories
        if len(active_memories) > 4:
            memories = active_memories[-4:]
        memory = Memory(0)
        memory.virtual_type = virtual_type
        memory.children = memories
        memory = self.add_memory(memories)
        self.active_memories.append(memory)

    def compose_active_memories(self):
        vision_memories = [x for x in self.active_memories if x.physical_type == constants.VISION_FEATURE]
        self.compose_memory(constants.SLICE_MEMORY, vision_memories)
        sound_memories = [x for x in self.active_memories if x.physical_type == constants.SOUND_FEATURE]
        self.compose_memory(constants.SLICE_MEMORY, sound_memories)
        slice_memories = [x for x in self.active_memories if x.virtual_type == constants.SLICE_MEMORY]
        self.compose_memory(constants.INSTANT_MEMORY, slice_memories)
        instant_memories = [x for x in self.active_memories if x.virtual_type == constants.INSTANT_MEMORY]
        self.compose_memory(constants.SHORT_MEMORY, instant_memories)
        short_memories = [x for x in self.active_memories if x.virtual_type == constants.SHORT_MEMORY]
        self.compose_memory(constants.LONG_MEMORY, short_memories)
        long_memories = [x for x in self.active_memories if x.virtual_type == constants.LONG_MEMORY]
        self.compose_memory(constants.LONG_MEMORY, long_memories)

    def cleanup_active_memories(self):
        self.memories = set(x for x in self.memories if x.live)
        new_active_memories = set()
        for memory in self.active_memories:
            if memory.live:
                new_active_memories.add(memory)
            else:
                memory.deactivate()
        self.active_memories = new_active_memories

    def find_one_memory(self, memory):
        for x in self.memories:
            if memory.alike(x):
                return x
        return None

    def add_memory(self, memory):
        memory = self.find_one_memory(memory)
        if not memory:
            self.memory_id_sequence += 1
            memory.mid = self.memory_id_sequence
            self.memories.add(memory)
        return memory

    # Use a separate thread to cleanup memories regularly.
    def cleanup_memories(self):
        for memory in self.memories:
            memory.refresh()
        new_memories = set(x for x in self.memories if x.live)
        self.memories = new_memories

    # Use a separate thread to persist memories to storage regularly.
    def persist_memories(self):
        pass
