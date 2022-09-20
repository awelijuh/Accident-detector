import os

import cv2
import numpy as np

from Yolov5_StrongSORT_OSNet.yolov5.utils.augmentations import letterbox
from config.provider import get_conf
from database_module import map_service
from my_utils import TimeMeter

conf = get_conf().detect

PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.join(PATH, os.pardir, os.pardir)


class LoadMedia:
    # YOLOv5 image/video dataloader, i.e. `python detect.py --source image.jpg/vid.mp4`
    def __init__(self, img_size=640, stride=32, auto=True):
        self.path = os.path.join(ROOT_PATH, conf.image_path)
        # self.path = '../images'
        self.img_size = img_size
        self.stride = stride
        self.auto = auto
        self.cap = None
        self.last_image = None

        self.mask = None
        # self.mask = cv2.imread('mask.png', 0)
        # contours, hierarchy = cv2.findContours(self.mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # cnt = contours[0]
        # self.x, self.y, self.w, self.h = cv2.boundingRect(cnt)
        self.meter = TimeMeter('read_image')

        self.stream = cv2.VideoCapture('http://localhost:8081/stream')

    def __iter__(self):
        self.count = 0
        return self

    def get_filename(self):
        result = map_service.get_last_image()
        if result is None:
            return None
        return result.decode('utf-8')
        # files = os.listdir(self.path)
        # if files is None or len(files) == 0:
        #     return None
        # return max(files)

    def __next__(self):
        while True:
            # filename = self.get_filename()
            # while filename is None or filename == self.last_image:
            #     time.sleep(0.01)  # TODO бред
            #     filename = self.get_filename()

            # path = self.path + '/' + filename

            # if not os.path.exists(path):
            #     print(f'{path} not found')
            #     time.sleep(0.01)  # TODO бред
            #     continue

            # Read image
            self.count += 1
            # img0 = cv2.imread(path)  # BGR
            self.meter.start()
            # img0 = np.asarray(bytearray(map_service.get_image('image')), dtype=np.uint8)
            # ret, img0 = self.stream.read()
            ret, img0 = self.stream.read()
            self.meter.end()
            if img0 is None:
                continue
            # img0 = cv2.imdecode(img0, cv2.IMREAD_COLOR)

            # img0 = numpy.fromstring(self.redis.get('last_img'))
            if self.mask is not None:
                img0 = cv2.bitwise_and(img0, img0, mask=self.mask)
                img0 = img0[self.y:self.y + self.h, self.x:self.x + self.w]
            if img0 is None:
                continue
            # s = filename

            # Padded resize
            img = letterbox(img0, self.img_size, stride=self.stride, auto=self.auto)[0]

            # Convert
            img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
            img = np.ascontiguousarray(img)

            return img, img0, self.cap

    def new_video(self, path):
        self.frame = 0
        self.cap = cv2.VideoCapture(path)
        self.frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def __len__(self):
        return self.nf  # number of files
