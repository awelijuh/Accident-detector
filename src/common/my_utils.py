import time

import cv2
import requests


def resize_to_height(img, height):
    if height is None:
        return img
    height = int(height)
    width = img.shape[1]  # keep original width
    old_height = img.shape[0]
    width = int(width * height / old_height)
    return cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)


class TimeMeter:

    def __init__(self, name):
        self.name = name
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def end(self):
        if self.start_time is None:
            return
        tm = time.time()
        print(f'{tm}: operation {self.name}: {tm - self.start_time}')
        self.start_time = None


def put_image(img):
    resp = requests.post('http://localhost:8000/api/put_image', data=img)
    print(resp)
