from enum import Enum


class MediaStatusEnum(Enum):
    Accepted = "ACCEPTED"
    NotFound = 'NOT FOUND'
    Processing = 'PROCESSING'
    Rejected = 'REJECTED'
    Done = 'DONE'
