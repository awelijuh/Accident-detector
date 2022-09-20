from redis import Redis

from config.provider import get_conf

redis_conf = get_conf()

print(redis_conf)

redis_conf = redis_conf.redis


def get_redis_db():
    return Redis(host=redis_conf.host, port=redis_conf.port, db=redis_conf.db)
