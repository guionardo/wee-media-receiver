import json
from datetime import datetime
from typing import List

from src.dto.media_status_enum import MediaStatusEnum


class MediaData:

    __slots__ = ['post_id', 'media_id', 'creation_date', 'media_path', 'new_media_path',
                 'category', 'notification_sent', 'notification_accepted', 'status', 'new_media_id']

    CREATE_TABLE_SQL = '''
CREATE TABLE IF NOT EXISTS media (
    post_id INTEGER NOT NULL,
    media_id TEXT NOT NULL,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    media_path TEXT NOT NULL,
    new_media_path TEXT NOT NULL,
    category TEXT NULL,
    notification_sent INTEGER DEFAULT 0,
    notification_accepted INTEGER DEFAULT 0,
    status TEXT NULL,
    new_media_id TEXT NOT NULL,
    CONSTRAINT media_PK PRIMARY KEY (post_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS media_media_path_IDX ON media (media_path);
            '''

    def __init__(self, row: tuple = None, **fields):
        """MediaData fields
        post_id: int
        media_id: str
        creation_date: datetime
        media_path: str
        new_media_path: str
        category: dict
        notification_sent: int
        notification_accepted: int
        status: str
        new_media_id: str
        """
        if not isinstance(row, tuple):
            row = (0, '', datetime.now(), '', '', None, 0, 0, '', '')
        if len(row) != len(self.__slots__):
            raise ValueError('Invalid row', row)
        self.post_id: int = fields.get('post_id', row[0])
        self.media_id: int = fields.get('media_id', row[1])
        self.creation_date: datetime = fields.get('creation_date', row[2])
        if isinstance(self.creation_date, str):
            self.creation_date = datetime.strptime(
                self.creation_date, '%Y-%m-%d %H:%M:%S.%f')
        self.media_path: str = fields.get('media_path', row[3])
        self.new_media_path: str = fields.get('new_media_path', row[4])
        self.category = fields.get('category', row[5])
        if isinstance(self.category, str) and self.category:
            self.category = json.loads(self.category)
        elif not isinstance(self.category, dict):
            self.category = {}
        self.notification_sent = fields.get('notification_sent', row[6])
        self.notification_accepted = fields.get(
            'notification_accepted', row[7])
        self.status = fields.get('status', row[8])
        if isinstance(self.status, str) and self.status:
            self.status = MediaStatusEnum(self.status)
        self.new_media_id = fields.get('new_media_id', row[9])

    def as_row(self) -> tuple:
        return (self.post_id,
                self.media_id,
                self.creation_date,
                self.media_path,
                self.new_media_path,
                json.dumps(self.category),
                self.notification_sent,
                self.notification_accepted,
                self.status.value,
                self.new_media_id)

    @classmethod
    def field_names(cls) -> List[str]:
        return cls.__slots__

    @classmethod
    def field_names_sql(cls) -> str:
        return ','.join(cls.__slots__)

    @classmethod
    def field_values_placeholders(cls) -> str:
        return ','.join(['?'] * len(cls.__slots__))
