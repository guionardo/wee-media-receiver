import os
from typing import List

import cv2


def extract_video_frames(video_file_name: str,
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
