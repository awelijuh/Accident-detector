import os
import threading
import time

import cv2
import numpy
from flask import Flask, Response

from common.my_utils import resize_to_height, TimeMeter
from config.provider import get_conf

PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.join(PATH, os.pardir, os.pardir)

saver_conf = get_conf().capture.saver

app = Flask(__name__)
port = 8081

image = None


def gen_stream():
    global image
    if image is None:
        return
    while True:
        (flag, encodedImage) = cv2.imencode(f".{saver_conf.image_format}", image)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg' + b'\r\n\r\n' + bytearray(
            encodedImage) + b'\r\n')


@app.get('/stream')
def stream():
    return Response(gen_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.get('/image')
def image():
    return Response(cv2.imencode(f'.{saver_conf.image_format}', image)[1].tobytes())


threading.Thread(target=lambda: app.run('0.0.0.0', port, debug=True, use_reloader=False)).start()


class FrameSaver:
    def __init__(self, fps, width, height):
        if not os.path.exists(saver_conf.image_path):
            os.makedirs(saver_conf.image_path)
        if not os.path.exists(saver_conf.video_path):
            os.makedirs(saver_conf.video_path)

        self.fps = fps
        self.width = width
        self.height = height
        self.video_writer = None
        self.video_start = None
        self.time_meter = TimeMeter('save_image')

    def create_writer(self, tt):
        fourcc = cv2.VideoWriter_fourcc(*'DIVX')
        # fourcc = -1
        self.video_writer = cv2.VideoWriter(os.path.join(ROOT_PATH, f'{saver_conf.video_path}/{tt}.avi'), fourcc, 25,
                                            (self.width, self.height))
        self.video_start = tt

    def next_frame(self, frame: numpy.ndarray):
        global image
        t = time.time()
        image_name = f'{t}.{saver_conf.image_format}'

        # cv2.imwrite(os.path.join(ROOT_PATH, saver_conf.image_path, image_name), frame)
        # self.time_meter.start()
        # put_image(cv2.imencode(f'.{saver_conf.image_format}', frame)[1].tobytes())
        # map_service.set_image(cv2.imencode(f'.{saver_conf.image_format}', frame)[1].tobytes())
        image = frame
        # self.time_meter.end()
        # set_last_image(image_name)

        # images = os.listdir(os.path.join(ROOT_PATH, saver_conf.image_path))
        # images.sort(reverse=True)
        # for frame_to_remove in images[int(saver_conf.max_images):]:
        #     os.remove(os.path.join(ROOT_PATH, saver_conf.image_path, frame_to_remove))

        if not saver_conf.video_enable:
            return
        if self.video_writer is None:
            self.create_writer(t)

        self.video_writer.write(resize_to_height(frame, None))

        if t - self.video_start >= saver_conf.video_duration:
            self.video_writer.release()
            self.video_writer = None
            print(f'release {self.video_start} - {t}, d: {t - self.video_start}')

            videos = os.listdir(os.path.join(ROOT_PATH, saver_conf.video_path))
            videos.sort(reverse=True)
            for video_to_remove in videos[saver_conf.max_videos:]:
                os.remove(os.path.join(ROOT_PATH, saver_conf.video_path, video_to_remove))
