import logging
import os
import shutil
import tempfile
import time
from typing import List, Union

import cv2
import tensorflow as tf
import tensorflow_hub as hub
from src.dto.get_video_response import GetVideoResponse
from src.dto.video_categories import VideoCategory
from tensorflow import keras

models = [
    module
    for module in os.listdir(
        os.path.join(os.path.dirname(__file__), 'models', '*'))]

IMAGE_DIM = 224   # required/default image dimensionality


class ModelProcessor:
    MODELS = {}

    def __init__(self, media_id: str, video_filename: str):
        self._log = logging.getLogger(__name__)
        self.model = self._load_model(models[0])
        self.media_id = media_id
        if not os.path.isfile(video_filename):
            raise FileNotFoundError(video_filename)
        self.video_filename = video_filename

    def __call__(self, *args, **kwds) -> Union[GetVideoResponse, None]:
        return self.process(self.media_id, self.video_filename)

    def _load_model(self, model_path: str):
        model = self.MODELS.get(model_path)
        if model:
            return model
        if model_path is None or not os.path.isfile(model_path):
            raise ValueError(
                "saved_model_path must be the valid directory of a saved model to load.")

        model = tf.keras.models.load_model(
            model_path,
            custom_objects={'KerasLayer': hub.KerasLayer},
            compile=False)
        self.MODELS[model_path] = model
        return model

    def process(self, media_id: str, video_filename: str) -> Union[GetVideoResponse, None]:
        """Process video file"""
        if not os.path.isfile(video_filename):
            return
        video_size = os.path.getsize(video_filename)
        try:
            start_time = time.time()
            tmp = tempfile.mkdtemp(suffix='vp')
            frames = self._extract_video_frames(video_filename, 20, tmp)
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

    def _extract_video_frames(self, video_file_name: str,
                              n_frames: int, destiny_folder: str) -> List[str]:
        """Extract frames from video and saves into destiny folder
        Returns list of files for each frame"""
        video_file_name = os.path.abspath(video_file_name)
        if not os.path.isfile(video_file_name):
            raise FileNotFoundError(video_file_name)
        if not os.path.isdir(destiny_folder):
            raise FileNotFoundError(destiny_folder)

        vidcap = cv2.VideoCapture(video_file_name)
        skip = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT)/n_frames)
        frame = 0

        success = True
        files = []
        while success:
            vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame*skip)
            frame += 1
            success, image = vidcap.read()
            if success:
                frame_file_name = os.path.join(
                    destiny_folder, f'frame_{frame:03}.jpg')
                if cv2.imwrite(frame_file_name, image):
                    files.append(frame_file_name)
            if frame >= n_frames:
                success = False

        return files

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

        model_preds = self._model.predict(nd_images)

        categories = ['drawings', 'hentai', 'neutral', 'porn', 'sexy']

        probs = []
        for _, single_preds in enumerate(model_preds):
            single_probs = {}
            for j, pred in enumerate(single_preds):
                single_probs[categories[j]] = round(float(pred), 6) * 100
            probs.append(single_probs)
        return probs
