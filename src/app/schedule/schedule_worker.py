import datetime
import logging
import threading
from queue import Empty, Queue
from typing import List, Protocol

from src.app.jobs import JobName
from src.config.config import Config
from src.repositories.media_repository import MediaRepository

q = Queue()  # Queue of JobItems


class Job(Protocol):

    _type: str
    _field_names: List[str]

    def _setup(self, type: str, *field_names):
        self._type = type
        self._field_names = field_names

    def _valid_event(self, event):
        return (
            event.get('type', None) == self._type and
            all(self.get_event_fields(event, *self._field_names)))

    def get_event_fields(self, event) -> list:
        return [event.get(field_name, None)
                for field_name in self._field_names]

    def can_log(self) -> bool:
        return True

    def can_process(self, event) -> bool:
        if event.get('type', None) != self._type:
            return False
        for field in self._field_names:
            if field not in event:
                return False
        return True

    def do_process(self, event, context) -> bool:
        ...

    def interval(self) -> datetime.timedelta:
        ...


class JobItem:
    _key = 0

    def __init__(self, job: Job):
        self.job = job
        self._key += 1
        self.key = self._key
        self.last_run = datetime.datetime(1970, 1, 1)

    def next_run(self) -> datetime.datetime:
        return self.last_run + self.job.interval()


class ScheduleWorker:

    def __init__(self, config: Config):
        self.jobs: List[JobItem] = []
        self._last_run = -1
        self._can_run = False
        self.config = config
        self.log = logging.getLogger(self.__class__.__name__)

    def add_job(self, job: Job):
        self.log.info('Added job %s', job.__class__.__name__)
        self.jobs.append(JobItem(job))

    def get_next_job(self, event) -> JobItem:
        for job in self.jobs:
            if job.job.can_process(event):
                return job

        return None

    def publish_event(self, event_type: str, **event):
        self.log.info('Publishing event %s', event_type)
        q.put(dict(type=event_type, **event), block=True)

    def run(self, **kwargs):
        queue = kwargs.get('q')
        self.log.info('ScheduleWorker started')
        ctx = ScheduleContext(self.config, self, MediaRepository(self.config))
        while self._can_run:
            try:
                event = queue.get(block=True, timeout=2)
                job_item = self.get_next_job(event)
                if job_item is None:
                    self.log.warning('No job found for event %s', event)
                    continue
                job = job_item.job

                if job.can_log():
                    self.log.info('Received event %s for job %s',
                                  event, job.__class__.__name__)

                if job.do_process(event, ctx):
                    if job.can_log():
                        self.log.info('Job %s processed event %s',
                                      job.__class__.__name__, event)
                else:
                    self.log.info('Job %s did not process event %s',
                                  job.__class__.__name__, event)
            except Empty:
                queue.put({'type': JobName.Renotify.value}, block=True)
                continue
            except Exception as exc:
                self.log.error('Error processing event %s: %s',
                               event, str(exc), exc_info=exc)

        self.log.info('SchedulerWorker stopped')
        exit(0)

    def start(self):
        if not self.jobs:
            self.log.warning('No jobs added')
            return
        self._can_run = True
        t = threading.Thread(target=self.run,
                             name='ScheduleWorker',
                             daemon=True,
                             kwargs=dict(q=q))
        self.log.info('ScheduleWorker starting')
        t.start()

    def stop(self):
        self._can_run = False
        self.log.info('ScheduleWorker is stopping')


class ScheduleContext:

    def __init__(self, config: Config,
                 schedule: ScheduleWorker,
                 media_repository: MediaRepository):
        self.config = config
        self.schedule = schedule
        self.repository = media_repository
