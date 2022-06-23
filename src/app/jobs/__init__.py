import enum


class JobName(enum.Enum):
    Analysis = 'analysis'
    Notify = 'notify'
    Optimize = 'optimize'
    ReceiveVideo = 'receive_video'
    RemoveVideo = 'remove_video'
    Renotify = 'renotify'
    Upload = 'upload'
