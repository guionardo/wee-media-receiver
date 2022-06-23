import unittest

from src.analysis.model_collection import ModelCollection


class TestModelCollection(unittest.TestCase):

    def test(self):
        model_collection = ModelCollection()
        self.assertIsNotNone(ModelCollection._model_file)
        model = model_collection.get_model()
        self.assertIsNotNone(model)
