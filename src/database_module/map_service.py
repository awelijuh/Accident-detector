import json
import time
from typing import Optional

from redis import Redis

from database_module import redis_constants
from database_module.redis_db import get_redis_db

redis_db: Optional[Redis] = None


def init_redis():
    global redis_db
    if redis_db is None:
        redis_db = get_redis_db()


def cast_or_none(m_type, value):
    try:
        return m_type(value)
    except Exception:
        return None


def set_fps(fps):
    init_redis()
    redis_db.set(redis_constants.CAPTURE_READ_FPS, str(fps))


def get_fps():
    init_redis()
    return cast_or_none(float, redis_db.get(redis_constants.CAPTURE_READ_FPS))


def set_to_redis(key, value):
    init_redis()
    redis_db.set(key, value)


def get_from_redis(key):
    init_redis()
    return redis_db.get(key)


class ImageProcessor:

    def __init__(self, key):
        self.key = key
        self.max_images = 20

    def get_current_index(self):
        current_index = cast_or_none(int, get_from_redis(f'{redis_constants.CURRENT_IMAGE_INDEX}_{self.key}'))
        if current_index is None:
            return 0
        return current_index

    def set_current_index(self, index):
        set_to_redis(f'{redis_constants.CURRENT_IMAGE_INDEX}_{self.key}', str(index))
        set_to_redis(f'{redis_constants.CURRENT_IMAGE_TIME}_{self.key}', str(time.time()))

    def get_time(self):
        return cast_or_none(str, get_from_redis(f'{redis_constants.CURRENT_IMAGE_TIME}_{self.key}'))

    def add_image(self, img):
        # next_index = (self.get_current_index() + 1) % self.max_images
        # set_to_redis(f'{self.key}_{next_index}', img)
        set_to_redis(f'{self.key}', img)
        # self.set_current_index(next_index)

    def get_image(self):
        # return get_from_redis(f'{self.key}_{self.get_current_index()}')
        return get_from_redis(f'{self.key}')


images = {
    'image': ImageProcessor(redis_constants.READ_FRAME),
    'detect': ImageProcessor(redis_constants.DETECT_FRAME)
}


def set_last_image(img):
    set_to_redis(redis_constants.CAPTURE_LAST_IMAGE, img)


def get_last_image():
    return get_from_redis(redis_constants.CAPTURE_LAST_IMAGE)


def set_last_detect(img):
    set_to_redis(redis_constants.LAST_DETECT, img)


def set_detect_benchmark(value):
    s = json.dumps(value)
    set_to_redis(redis_constants.DETECT_BENCHMARK, s)


def get_detect_benchmark():
    init_redis()
    s = redis_db.get(redis_constants.DETECT_BENCHMARK)
    try:
        return json.loads(s)
    except Exception:
        return None


def set_image(frame):
    init_redis()
    images['image'].add_image(frame)


def get_time(key):
    return images[key].get_time()


def get_image(key):
    return images[key].get_image()


def set_detect_image(frame):
    init_redis()
    return images['detect'].add_image(frame)

# def set_fps(fps):
#     db: Session = SessionLocal()
#     if db.query(Preference).where(Preference.key == PREFERENCE_FPS).first() is None:
#         db.add(Preference(key=PREFERENCE_FPS, value=str(fps)))
#     else:
#         db.execute(update(Preference).where(Preference.key == PREFERENCE_FPS).values(value=str(fps)))
#     db.commit()
#     db.flush()
#     db.close()


# def get_fps():
#     db: Session = SessionLocal()
#     result = db.query(Preference).where(Preference.key == PREFERENCE_FPS).first()
#     fps = None
#     if result is not None:
#         fps = result.value
#     db.close()
#
#     return fps
