import os
import logging
import tensorflow as tf
import tensorflow_hub as hub

_MODEL = None


class ModelCollection:

    _model_file = ''

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        if self._model_file:
            return
        models_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 'models'))
        for module in os.listdir(models_path):
            self._model_file = os.path.join(models_path, module)
        self.log.info('Available model: %s', self._model_file)

    def get_model(self):
        global _MODEL
        if not _MODEL:
            self.log.info(
                'Loading model: %s', self._model_file)
            _MODEL = tf.keras.models.load_model(
                self._model_file,
                custom_objects={'KerasLayer': hub.KerasLayer},
                compile=False)

        return _MODEL
