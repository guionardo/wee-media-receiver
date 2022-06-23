from src.app.jobs.analysis_job import AnalysisJob
from src.app.jobs.notify_job import NotifyJob
from src.app.jobs.optimize_job import OptimizeJob
from src.app.jobs.receive_video_job import ReceiveVideoJob
from src.app.jobs.remove_video_job import RemoveVideoJob
from src.app.jobs.renotify_job import RenotifyJob
from src.app.jobs.upload_job import UploadJob
from src.app.schedule.schedule_worker import ScheduleWorker
from src.config.config import Config


def get_scheduler(config: Config) -> ScheduleWorker:
    scheduler = ScheduleWorker(config)

    scheduler.add_job(ReceiveVideoJob())
    scheduler.add_job(NotifyJob())
    scheduler.add_job(AnalysisJob())
    scheduler.add_job(OptimizeJob())
    scheduler.add_job(UploadJob())
    scheduler.add_job(RenotifyJob())
    scheduler.add_job(RemoveVideoJob())

    return scheduler
