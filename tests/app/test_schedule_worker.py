import unittest

from src.app.schedule.schedule_worker import Job


class TestingJob(Job):

    def __init__(self):
        self._setup('testing', 'filename', 'filesize')


class TestScheduleWorker(unittest.TestCase):

    def test_can_do_job(self):
        job = TestingJob()
        self.assertTrue(job.can_process(
            dict(type='testing', filename='', filesize=0)))

    def test_cannot_do_job(self):
        job = TestingJob()
        self.assertFalse(job.can_process(dict(type='testing', filename='')))
