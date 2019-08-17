from . import constants
import time


class Memory:
    DURATION_SLICE = 0.15
    DURATION_INSTANT = 0.5
    DURATION_SHORT = 3
    DURATION_LONG = 360

    live = True
    recall_count = 0
    last_recall_time = 0
    reward = 0
    protect_time = 0
    virtual_type = None
    physical_type = None
    parent = None
    children = None

    # for active period
    status = None
    last_activate_time = None
    matched_time = None
    active_start_time = None
    active_end_time = None

    def __init__(self, mid):
        self.mid = mid

    def __hash__(self):
        return int(self.mid)

    def __eq__(self, other):
        return other == self.mid

    # def __eq__(self, other):
    #     return self.__dict__ == other

    def refresh(self):
        pass

    def activate(self):
        if self.status == constants.MATCHING:
            return

        self.status = constants.MATCHING
        self.active_start_time = time.time()
        self.last_activate_time = time.time()

        if self.virtual_type == constants.SLICE_MEMORY:
            self.active_end_time = time.time() + self.DURATION_SLICE
        elif self.virtual_type == constants.INSTANT_MEMORY:
            self.active_end_time = time.time() + self.DURATION_INSTANT
        elif self.virtual_type == constants.SHORT_MEMORY:
            self.active_end_time = time.time() + self.DURATION_SHORT
        elif self.virtual_type == constants.LONG_MEMORY:
            self.active_end_time = time.time() + self.DURATION_LONG

    def activate_tree(self):
        self.activate()
        for memory in self.children:
            if memory.virtual_type in [constants.LONG_MEMORY, constants.SHORT_MEMORY, constants.INSTANT_MEMORY]:
                if memory.status != constants.MATCHING:
                    memory.activate_tree()
                    # only one child will be matching status
                    break
            else:
                memory.activate_tree()

    def match(self):
        if self.status != constants.MATCHING:
            return False

        for memory in self.children:
            if memory.status != constants.MATCHED:
                return False

        self.status = constants.MATCHED
        self.recall()
        return True

    def recall(self):
        return

    def alike(self, memory):
        if memory.children:
            if self.children != memory.children:
                return False
        return True

    def deactivate(self):
        self.status = None
        self.active_start_time = None
        self.active_end_time = None

    def is_live(self):
        return self.live

    def destroy(self):
        self.live = False
