from typing import List

from redis import Redis

from config.settings import REDIS
from controller.context_manager import context_log_meta
from logger import logger
from utils.utils import Singleton


@Singleton
class Cache:
    def __init__(self):
        self.__redis_url = REDIS.url
        self._redis = self.__init_redis()

    def __init_redis(self):
        try:
            redis = Redis.from_url(
                self.__redis_url, encoding="utf-8", decode_responses=True)
        except Exception as e:
            logger.error(f"error in initiating redis in non cluster mode for url : {self.__redis_url} error : {e}")
            return None
        return redis

    def __validate(self, key='default_valid') -> bool:
        if not (self._redis and key):
            return False
        return True

    def set(self, key: str, value: str, expiry_in_seconds=None, nx=False) -> bool:
        try:
            if not self.__validate(key=key):
                return False
            self._redis.set(key, value, ex=expiry_in_seconds, nx=nx)
            return True
        except Exception as e:
            logger.error(extra=context_log_meta.get(), msg=f"error in redis set : {e}")
            return False

    def get(self, key: str) -> str:
        try:
            if not self.__validate(key=key):
                return None
            return self._redis.get(key)
        except Exception as e:
            logger.error(extra=context_log_meta.get(), msg=f"error in redis get : {e}")
            return None

    def delete(self, key: str) -> int:
        try:
            if not self.__validate(key=key):
                return None
            return self._redis.delete(key)
        except Exception as e:
            logger.error(extra=context_log_meta.get(), msg=f"error in redis delete : {e}")
            return None

    def sadd(self, key: str, values: List[str]) -> int:
        try:
            if not self.__validate(key=key):
                return 0
            return self._redis.sadd(key, *values)
        except Exception as e:
            logger.error(msg=f"error in redis sadd : {e}")
            return 0

    def srem(self, key: str, values: List[str]) -> int:
        try:
            if not self.__validate(key=key):
                return 0
            return self._redis.srem(key, *values)
        except Exception as e:
            logger.error(msg=f"error in redis srem : {e}")
            return 0

    def srandmember(self, key: str) -> str:
        try:
            if not self.__validate(key=key):
                return None
            return self._redis.srandmember(key)
        except Exception as e:
            logger.error(msg=f"error in redis srandmember : {e}")
            return None

    def increment(self, key: str, amount=1) -> int:
        try:
            if not self.__validate(key=key):
                return 0
            return self._redis.incr(key, amount)
        except Exception as e:
            logger.error(msg=f"error in redis increment : {e}")
            return 0
