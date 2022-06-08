import json
import logging
import urllib.parse

import urllib3
from src.config.config import Config
from src.dto.media_notification import MediaNotification


class BackendAPI:

    http: urllib3.PoolManager

    def __init__(self, config: Config):
        self.log = logging.getLogger(self.__class__.__name__)
        self.backend_url = config.backend_url
        if self.backend_url:
            self.http = urllib3.PoolManager(headers={'Content-Type': 'application/json',
                                                     'X-WeeMedia-Auth': config.backend_auth})
        else:
            self.http = None
        self._use_form = False

    def is_available(self):
        return bool(self.backend_url)

    def notify_backend(self, notification: MediaNotification) -> bool:
        """Send notification of processed media to backend
        Returns true if accepted"""
        body = json.dumps(notification.as_dict()).encode('utf-8')
        try:
            if self._use_form:
                data = {"grant_type": "password", "client_id": "<client_ID>",
                        "client_secret": "<client_Secret>", "username": "<username>", "password": "<password>"}

                data = urllib.parse.urlencode(data)

                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                r = self.http.request(
                    'POST', self.backend_url,
                    headers=headers, body=data)
            else:
                r = self.http.request('POST', self.backend_url, body=body)
            if r.status not in [200, 202]:
                self.log.warning('Notifying backend %s -> %s:%s',
                                 body, r.status, r.data.decode('utf-8'))

                return False

            response = json.loads(r.data.decode('utf-8'))
            if isinstance(response, dict) and response.get('status') == 'accepted':
                self.log.info('Notifying backend %s -> %s', body, response)
                return True

            self.log.warning('Notifying backend %s -> %s:%s',
                             body, r.status, r.data.decode('utf-8'))

        except Exception as exc:
            self.log.error('Notifying backend %s -> %s', body, exc)

        return False
