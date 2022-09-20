import time

import cv2

from common.my_utils import TimeMeter
from config.provider import get_conf
from database_module.map_service import set_fps
from saver import FrameSaver
from stream import get_stream

conf = get_conf().capture


class Capturer:
    def __init__(self):
        self.stream = get_stream()
        # self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 0)
        # cv2.CAP_PROP_VIDEO_STREAM
        cap = self.stream
        self.fps = conf.capture_fps
        if self.fps is None:
            self.fps = float(cap.get(cv2.CAP_PROP_FPS))

        self.frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_size = (self.frame_width, self.frame_height)

        print('FPS:', self.fps)
        print('FRAME_SIZE:', self.frame_size)
        self.wt = 1 / self.fps

        self.last_save_image_time = 0

        self.start_recording_time = time.time()
        self.frame_start_recording_time = self.start_recording_time

        self.none_frame_count = 0  # число пустых фреймов
        self.none_frame_to_restart_count = 10  # через сколько пустых фреймов перезапустить стрим
        self.restart_count = 0  # число сделаных перезапусков
        self.restart_none_frame_to_finish_count = 10000  # через сколько неудачных перезапусков завешить программу

        self.real_fps = 0
        self.is_road = None

        self.saver = FrameSaver(self.fps, self.frame_width, self.frame_height)

        self.meter = TimeMeter('capture_image')

    def start_road(self):
        self.is_road = True
        while self.is_road:
            self.next_frame()

    def next_frame(self):
        start_time = time.time()

        # self.meter.start()
        ret, frame = self.stream.read()
        # self.meter.end()

        if frame is not None:

            t = time.time()
            self.saver.next_frame(frame)

            self.real_fps = (1 / (t - self.last_save_image_time))

            set_fps(self.real_fps)

            self.last_save_image_time = t

            self.none_frame_count = 0
            self.restart_count = 0
            self.last_save_image_time = time.time()
            dt = self.last_save_image_time - start_time
            if self.wt - dt > 0:
                time.sleep(self.wt - dt)
        else:
            print('frame None')
            self.none_frame_count += 1
            set_fps(0)

        if self.restart_count >= self.restart_none_frame_to_finish_count:
            self.is_road = False
            set_fps(0)
            return

        if self.none_frame_count >= self.none_frame_to_restart_count:
            self.stream = get_stream()
            self.none_frame_count = 0
            self.restart_count += 1
            set_fps(0)
            time.sleep(4)
