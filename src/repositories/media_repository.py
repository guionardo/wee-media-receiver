import logging
import sqlite3
import threading
from typing import List

from src.config.config import Config
from src.domain.media_data import MediaData


class MediaRepository:

    def __init__(self, config: Config):
        self.log = logging.getLogger(self.__class__.__name__)
        self.lock = threading.Lock()
        self.conn: sqlite3.Connection
        self._setup(config.local_db)

    def _setup(self, local_db: str):
        try:
            self.lock.acquire()
            self.conn = sqlite3.connect(local_db)
            self.conn.executescript(MediaData.CREATE_TABLE_SQL)
            self.log.info('MediaRepository initialized: %s', local_db)
        except Exception as exc:
            self.log.error('Failed to initialize MediaRepository: %s', exc)
            raise
        finally:
            self.lock.release()

    def get_media(self, media_id: int) -> MediaData:
        result: MediaData = None
        try:
            self.lock.acquire()
            sql = f'SELECT {MediaData.field_names_sql()} FROM media WHERE media_id = ?'
            row = self.conn.execute(sql, (media_id,)).fetchone()
            if row:
                result = MediaData(row)
            # for row in self.conn.execute('SELECT media_id,creation_date,media_path,new_media_path,category,notification_sent,notification_accepted FROM media WHERE media_id = :media_id', dict(media_id=media_id)):
            #     result = MediaData(row)
            #     break
        except Exception as exc:
            self.log.error('Failed to get media %s: %s', media_id, exc)
        finally:
            self.lock.release()
        return result

    def set_media(self, media_data: MediaData) -> bool:
        result: bool = False
        try:
            self.lock.acquire()
            sql = f'INSERT OR REPLACE INTO media ({MediaData.field_names_sql()}) VALUES ({MediaData.field_values_placeholders()})'
            params = media_data.as_row()
            self.conn.execute(sql, params)
            self.conn.commit()
            result = True
        except Exception as exc:
            self.log.error('Failed to set media %s: %s',
                           media_data.media_id, exc)
        finally:
            self.lock.release()
        return result

    def get_unnotified_media(self, limit: int = 5) -> List[MediaData]:
        result = []
        try:
            self.lock.acquire()
            for row in self.conn.execute(
                f'SELECT {MediaData.field_names_sql()} '
                'FROM media '
                'WHERE notification_accepted=0 '
                'ORDER BY notification_sent ASC, creation_date ASC '
                    f'LIMIT {limit}'):
                result.append(MediaData(row))
        except Exception as exc:
            self.log.error('Failed to get unnotified media: %s', exc)
        finally:
            self.lock.release()
        return result
