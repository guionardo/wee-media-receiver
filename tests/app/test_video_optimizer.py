import logging
import unittest
from src.app.video_optimizer import VideoOptimizer


class TestVideoOptimizer(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        logging.basicConfig(level=logging.DEBUG, format=logging.BASIC_FORMAT)
        return super().setUpClass()

    def test(self):
        with VideoOptimizer('uploads/2022/06/test_1', 'olha.mp4') as vo:
            vo.run()
            self.assertEqual('uploads/2022/06/test_1.webm', vo.new_media_id())
