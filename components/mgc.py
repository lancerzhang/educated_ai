from . import constants
from . import util
from .data_adaptor import DataAdaptor
from .data_sqlite3 import DataSqlite3
from enum import Enum
import copy
import logging
import time

logger = logging.getLogger('mgc')
logger.setLevel(logging.INFO)


class Job:
    job_type = None
    job_serial = 0
    job_content = None

    def __init__(self, job_type, job_serial):
        self.job_type = job_type
        self.job_serial = job_serial


class JobType(Enum):
    UPDATE_PM = 0
    UPDATE_CM = 1
    DELETE_BM = 2
    DELETE_VISION = 3
    DELETE_SOUND = 4
    DELETE_ID = 5
    DELETE_VIRTUAL = 6  # TODO, delete virtual memory without children
    PERSIST = 7


class GC:
    running = True
    INTERVAL = 1
    jobs = []
    current_index = 0
    current_job = None

    @util.timeit
    def init_jobs(self):
        for i in range(10):
            self.jobs.append(Job(JobType.UPDATE_PM, i))
        for i in range(10):
            self.jobs.append(Job(JobType.UPDATE_CM, i))
        for i in range(10):
            self.jobs.append(Job(JobType.DELETE_BM, i))
        self.jobs.append(Job(JobType.DELETE_VISION, 0))
        self.jobs.append(Job(JobType.DELETE_SOUND, 0))
        self.jobs.append(Job(JobType.DELETE_ID, 0))
        self.jobs.append(Job(JobType.PERSIST, 0))

    @util.timeit
    def __init__(self):
        self.data = DataAdaptor(DataSqlite3('data/dump.sql', init=False))
        self.init_jobs()

    @util.timeit
    def prepare(self):
        while self.running:
            time.sleep(self.INTERVAL)
            job = copy.copy(self.jobs[self.current_index])
            if job.job_type == JobType.UPDATE_PM:
                selected_memories = self.data.get_memories_by_id_mod(job.job_serial)
                job.job_content = self.data.search_invalid_fields(selected_memories, constants.PARENT_MEM)
            elif job.job_type == JobType.UPDATE_CM:
                selected_memories = self.data.get_memories_by_id_mod(job.job_serial)
                job.job_content = self.data.search_invalid_fields(selected_memories, constants.CHILD_MEM)
            elif job.job_type == JobType.DELETE_BM:
                selected_memories = self.data.get_memories_by_id_mod(job.job_serial)
                job.job_content = self.data.search_invalid_memories(selected_memories)

            self.current_job = job
            self.current_index += 1
            if self.current_index == len(self.jobs):
                self.current_index = 0

    @util.timeit
    def execute(self):
        if not self.current_job:
            return
        job = self.current_job
        self.current_job = None
        if job.job_type == JobType.DELETE_BM:
            self.data.delete_memories(job.job_content)
        elif job.job_type in [JobType.UPDATE_PM, JobType.UPDATE_CM]:
            self.data.update_memories(job.job_content)
        elif job.job_type == JobType.DELETE_SOUND:
            self.data.clean_sound_used_kernel()
        elif job.job_type == JobType.DELETE_VISION:
            self.data.clean_vision_used_kernel()
        elif job.job_type == JobType.DELETE_ID:
            self.data.clean_short_id()
        elif job.job_type == JobType.PERSIST:
            self.data.persist()
