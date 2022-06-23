from enum import Enum


class MediaStatusEnum(Enum):
    Accepted = 'ACCEPTED'
    Downloading = 'DOWNLOADING'
    Downloaded = 'DOWNLOADED'
    Analysing = 'ANALYSING'
    Analysed = 'ANALYSED'
    Optimizing = 'OPTIMIZING'
    Optimized = 'OPTIMIZED'
    Uploading = 'UPLOADING'
    Uploaded = 'UPLOADED'
    Notifying = 'NOTIFYING'
    Notified = 'NOTIFIED'
    NotFound = 'NOT FOUND'
    Processing = 'PROCESSING'
    Processed = 'PROCESSED'
    Rejected = 'REJECTED'
    Done = 'DONE'
