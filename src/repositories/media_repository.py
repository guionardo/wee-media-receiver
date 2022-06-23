import logging
import sqlite3
import threading
from typing import Dict, List

from src.config.config import Config
from src.domain.media_data import MediaData

singleton_repository = None


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

        except Exception as exc:
            self.log.error('Failed to get media %s: %s', media_id, exc)
        finally:
            self.lock.release()
        return result

    def get_media_by_postid(self, post_id: int) -> MediaData:
        result: MediaData = None
        try:
            self.lock.acquire()
            sql = f'SELECT {MediaData.field_names_sql()} FROM media WHERE post_id = ?'
            row = self.conn.execute(sql, (post_id,)).fetchone()
            if row:
                result = MediaData(row)

        except Exception as exc:
            self.log.error('Failed to get media %s: %s', post_id, exc)
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

    def delete_media(self, media_id: str) -> bool:
        result: bool = False
        try:
            self.lock.acquire()
            sql = 'DELETE FROM media WHERE media_id = ?'
            self.conn.execute(sql, (media_id,))
            self.conn.commit()
            result = True
        except Exception as exc:
            self.log.error('Failed to delete media %s: %s', media_id, exc)
        finally:
            self.lock.release()
        return result

    def get_media_status_count(self) -> Dict[str, int]:
        result = {}
        try:
            self.lock.acquire()
            sql = 'SELECT status, count(*) FROM media GROUP BY status'
            result = dict(self.conn.execute(sql).fetchall())
        except Exception as exc:
            self.log.error('Failed to get media status count: %s', exc)
        finally:
            self.lock.release()
        return result

    def get_latest_media(self, limit: int = 5) -> List[MediaData]:
        result = []
        try:
            self.lock.acquire()
            for row in self.conn.execute(
                f'SELECT {MediaData.field_names_sql()} '
                'FROM media '
                'ORDER BY creation_date DESC '
                    f'LIMIT {limit}'):
                result.append(MediaData(row))
        except Exception as exc:
            self.log.error('Failed to get latest media: %s', exc)
        finally:
            self.lock.release()
        return result


def get_repository(config: Config) -> MediaRepository:
    global singleton_repository
    if not singleton_repository:
        singleton_repository = MediaRepository(config)

    return singleton_repository
