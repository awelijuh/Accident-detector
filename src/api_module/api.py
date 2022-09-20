import os

import cv2
import fastapi
import numpy as np
from fastapi import FastAPI
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from common.my_utils import resize_to_height, TimeMeter
from config.provider import get_conf
from database_module import map_service
from database_module import service

PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.join(PATH, os.pardir, os.pardir)

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_conf = get_conf().api


@app.get('/api/benchmark')
def get_benchmarks():
    b = map_service.get_detect_benchmark()
    if b is None:
        b = {}
    read_fps = map_service.get_fps()
    if read_fps is not None:
        b['read_fps'] = read_fps
    return b


cash_images = {}


def gen_stream(path, redis_key='', size=None):
    meter = TimeMeter(f'get_frame({redis_key})')
    while True:
        # lst = os.listdir(path)
        # filename = max(lst)
        # filename = service.get_from_redis(redis_key).decode('utf-8')
        # frame = cv2.imread(os.path.join(ROOT_PATH, path, filename))
        bts = map_service.get_image(redis_key)
        if bts is not None:
            buff = np.asarray(bytearray(bts), dtype=np.uint8)
            # buff = buff.reshape(1, -1)
            frame = cv2.imdecode(buff, cv2.IMREAD_COLOR)
            # frame = buff
        else:
            frame = None
        if frame is not None:
            frame = np.copy(frame)

        if size is not None and frame is not None:
            frame = resize_to_height(frame, size)
        (flag, encodedImage) = cv2.imencode(f".{api_conf.image_format}", frame)
        meter.end()
        yield (b'--frame\r\n'
               b'Content-Type: image/' + api_conf.image_format.encode('utf-8') + b'\r\n\r\n' + bytearray(
            encodedImage) + b'\r\n')


@app.get('/api/stream')
def stream(type=None, size=None):
    if type == 'raw':
        return fastapi.responses.RedirectResponse(
            api_conf.image_url,
            status_code=status.HTTP_302_FOUND)
    elif type == 'detected':
        return fastapi.responses.RedirectResponse(
            api_conf.detect_url,
            status_code=status.HTTP_302_FOUND)
    # type_to_path = {
    #     'raw': api_conf.raw_path,
    #     'detected': api_conf.detected_path
    # }
    # type_to_redis_key = {
    #     'raw': 'image',
    #     'detected': 'detect',
    # }
    #
    # return StreamingResponse(gen_stream(type_to_path.get(type), type_to_redis_key.get(type), size=size),
    #                          media_type="multipart/x-mixed-replace;boundary=frame")


@app.get('/api/filterObjects')
def filterObjects(start_time=None, end_time=None, classes=None):
    return service.filter_delta_time(start_time, end_time, classes)


@app.get('/api/classes')
def get_all_classes(start_time=None, end_time=None):
    return service.get_all_class_names()


images = {}

app.mount("/", StaticFiles(directory=os.path.join(ROOT_PATH, "src/ui_module/build"), html=True), name="ui")
