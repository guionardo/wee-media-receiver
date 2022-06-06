import logging
import os
import shutil
import tempfile
import time
from typing import List, Union

import numpy as np
from src.dto.get_video_response import GetVideoResponse
from src.dto.video_categories import VideoCategory
from tensorflow import keras

from .model_collection import ModelCollection
from .video_capture import extract_video_frames


IMAGE_DIM = 224   # required/default image dimensionality


class VideoAnalyzer:
    MODELS = {}

    def __init__(self, media_id: str, video_filename: str):
        self.model_collection = ModelCollection()
        self._log = logging.getLogger(self.__class__.__name__)
        self.model = self.model_collection.get_model()
        self.media_id = media_id
        if not os.path.isfile(video_filename):
            raise FileNotFoundError(video_filename)
        self.video_filename = video_filename

    def __call__(self, *args, **kwds) -> Union[GetVideoResponse, None]:
        return self.process(self.media_id, self.video_filename)

    def process(self, media_id: str, video_filename: str) -> Union[GetVideoResponse, None]:
        """Process video file"""
        if not os.path.isfile(video_filename):
            return
        video_size = os.path.getsize(video_filename)
        try:
            start_time = time.time()
            tmp = tempfile.mkdtemp(suffix='vp')
            frames = extract_video_frames(video_filename, 20, tmp)
            prediction = self._predict(frames)
            shutil.rmtree(tmp)

            video_data = GetVideoResponse(
                video_id=media_id,
                categories=VideoCategory(**prediction['data']),
                message='OK',
                processing_time=time.time()-start_time
            )
            self._log.info('Processed video: %s', video_data)

        except Exception as exc:
            video_data = GetVideoResponse(
                video_id=media_id,
                message=str(exc)
            )

        return video_data

    def _predict(self, files: List[str]):
        image_preds = self._classify(files, IMAGE_DIM)
        return image_preds

    def _classify(self, input_paths, image_dim=IMAGE_DIM):
        """ Classify given a model, input paths (could be single string),
        and image dimensionality...."""
        images, _ = self._load_images(
            input_paths, (image_dim, image_dim))
        probs = self._classify_nd(images)
        return dict(zip(['data'], probs))

    def _load_images(self, image_paths, image_size):
        '''
        Function for loading images into numpy arrays for passing to model.predict
        inputs:
            image_paths: list of image paths to load
            image_size: size into which images should be resized
            verbose: show all of the image path and sizes loaded
        outputs:
            loaded_images: loaded images on which keras model can run predictions
            loaded_image_indexes: paths of images which the function is able to process
        '''
        loaded_images = []
        loaded_image_paths = []

        for img_path in image_paths:
            try:

                self._log.debug('_load_images -> %s size: %s',
                                img_path, image_size)

                image = keras.preprocessing.image.load_img(
                    img_path, target_size=image_size)
                image = keras.preprocessing.image.img_to_array(image)
                image /= 255
                loaded_images.append(image)
                loaded_image_paths.append(img_path)
            except Exception as ex:
                print("Image Load Failure: ", img_path, ex)

        return np.asarray(loaded_images), loaded_image_paths

    def _classify_nd(self, nd_images):
        """ Classify given a model, image array (numpy)...."""

        model_preds = self.model.predict(nd_images)

        categories = ['drawings', 'hentai', 'neutral', 'porn', 'sexy']

        probs = []
        for _, single_preds in enumerate(model_preds):
            single_probs = {}
            for j, pred in enumerate(single_preds):
                single_probs[categories[j]] = round(float(pred), 6) * 100
            probs.append(single_probs)
        return probs
