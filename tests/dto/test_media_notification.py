import unittest

from src.dto.media_notification import MediaNotification


class TestMediaNotification(unittest.TestCase):

    def test_0(self):
        metadata = {'wmr-status': 'OPTIMIZED',
                    'wmr-source': 'uploads/video/2021/December/0ba4b06178c056482ccf7ca326b3fc78-VID_20211025_210101555.mp4',
                    'wmr_analisys-drawings': '0.0327',
                    'wmr_analisys-hentai': '0.0104',
                    'wmr_analisys-neutral': '99.8486',
                    'wmr_analisys-porn': '0.0083',
                    'wmr_analisys-sexy': '0.1'}
        mn = MediaNotification(
            'media_id', 'media_id_new', 'TESTING', 1, metadata)
        self.assertEqual(0.01, mn.metadata['wmr-analisys-hentai'])
