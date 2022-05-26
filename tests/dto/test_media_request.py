import unittest

from src.dto.media_request import MediaRequestValidator


class TestMediaRequest(unittest.TestCase):

    def test(self):
        mr = MediaRequestValidator(
            'https://bomperfil2.us-east-1.linodeobjects.com/uploads/videos/2022/02/bomperfil_ebcd43699c167ecc21633f29a0da4643.mp4#t=0.01')
        self.assertEqual('bomperfil2', mr.bucket_name)
        self.assertEqual(
            '/videos/2022/02/bomperfil_ebcd43699c167ecc21633f29a0da4643.mp4', mr.media_id)
