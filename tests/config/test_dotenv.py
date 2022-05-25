import os
import unittest
from tempfile import NamedTemporaryFile

from src.config.dotenv import load_dotenv


class TestDotEnv(unittest.TestCase):

    def test_load_dotenv_file(self):
        with NamedTemporaryFile(mode='w+', delete=True) as file:
            file.write(
                'KEY_0=ABCD\nKEY_1=EFGH')
            file.flush()
            load_dotenv(filename=file.name)
        self.assertEqual('ABCD', os.environ.get('KEY_0'))
        self.assertEqual('EFGH', os.environ.get('KEY_1'))

    def test_load_dotenv_dict(self):
        load_dotenv(source=dict(KEY_2='ABCD', KEY_3='EFGH'))
        self.assertEqual('ABCD', os.environ.get('KEY_2'))
        self.assertEqual('EFGH', os.environ.get('KEY_3'))
