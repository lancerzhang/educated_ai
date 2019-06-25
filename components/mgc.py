from . import constants
import numpy as np
import time


class GC:
    KEEP_FIT_DURATION = 30
    PPS = constants.process_per_second
    DPS = 1.0 / constants.process_per_second
    cycle_names = [constants.EDEN, constants.YOUNG, constants.OLD]
    cycle_frames = np.array([0, 0, 0])
    cycle_gc = [False, False, False]
    cycle_threshold1 = [PPS * 5, PPS * 60 * 9, PPS * 60 * 19]
    cycle_threshold2 = [PPS * 8, PPS * 60 * 10, PPS * 60 * 21]

    def __init__(self, da):
        self.data = da
        da.full_gc()
        da.cleanup_fields()
        da.keep_fit()
        self.last_keep_fit_time = time.time()

    # as local database usually is single thread, we need carefully to handle it
    def process(self, duration):
        if time.time() - self.last_keep_fit_time > self.KEEP_FIT_DURATION:
            self.data.keep_fit()
            self.last_keep_fit_time = time.time()
            return

        frame_gc = False
        self.cycle_frames = self.cycle_frames + 1
        for i in range(0, len(self.cycle_names)):
            if not frame_gc and not self.cycle_gc[i]:
                if self.cycle_frames[i] < self.cycle_threshold1[i]:
                    if duration < self.DPS * 0.3:
                        self.data.gc(self.cycle_names[i])
                        self.cycle_gc[i] = True
                        frame_gc = True
                elif self.cycle_frames[i] < self.cycle_threshold2[i]:
                    if duration < self.DPS:
                        self.data.gc(self.cycle_names[i])
                        self.cycle_gc[i] = True
                        frame_gc = True
                else:
                    self.data.gc(self.cycle_names[i])
                    self.cycle_gc[i] = True
                    frame_gc = True
        for j in range(0, len(self.cycle_frames)):
            if self.cycle_frames[j] >= self.cycle_threshold2[j]:
                self.cycle_frames[j] = 0
                self.cycle_gc[j] = False
