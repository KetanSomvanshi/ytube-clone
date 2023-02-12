import http

import requests
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from config.constants import CacheKeys
from controller.context_manager import context_api_id, context_log_meta
from logger import logger
from models.base import GenericResponseModel


def build_api_response(generic_response: GenericResponseModel) -> JSONResponse:
    try:
        if not generic_response.api_id:
            generic_response.api_id = context_api_id.get()
        if not generic_response.status_code:
            generic_response.status_code = http.HTTPStatus.OK if not generic_response.errors \
                else http.HTTPStatus.UNPROCESSABLE_ENTITY
        response_json = jsonable_encoder(generic_response)
        res = JSONResponse(status_code=generic_response.status_code, content=response_json)
        logger.info(extra=context_log_meta.get(),
                    msg="build_api_response: Generated Response with status_code:"
                        + f"{generic_response.status_code}")
        return res
    except Exception as e:
        logger.error(extra=context_log_meta.get(), msg=f"exception in build_api_response error : {e}")
        return JSONResponse(status_code=generic_response.status_code, content=generic_response.errors)


def make_request(external_service_url, request_params: dict, method='GET', headers=None) -> (dict, int):
    try:
        request_headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        if headers is not None:
            request_headers.update(headers)
        response = requests.request(method=method, url=external_service_url, params=request_params,
                                    headers=request_headers, timeout=10)
        result_response, status_code = response.json(), response.status_code
        logger.debug(extra=context_log_meta.get(),
                     msg=f"make_request: Successfully made request to external service: {external_service_url}"
                         f" with status_code: {status_code} data= {result_response}")
        return result_response, status_code
    except Exception as e:
        logger.error(extra=context_log_meta.get(), msg=f"exception in make_request error : {e}")
        return {}, 500


class Singleton:
    """Implementation of singleton design pattern
    This is a singleton class which is used to get the instance of the class which is decorated with this class"""

    def __init__(self, cls):
        self._cls = cls

    def get_instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._cls()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `get_instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._cls)


class ApiLockManager:
    """This class is used to manage the api lock ,
    so that only one request can be processed at a time for a given api"""

    def __init__(self, api_run_id, expiry_in_seconds=600):
        self.cache_key = CacheKeys.LOCK_FOR_EXTERNAL_SYNC
        self.expiry_in_seconds = expiry_in_seconds
        self.api_run_id = api_run_id

    def acquire_lock_for_api(self) -> bool:
        from data_adapter.redis import Cache

        """ Check if the request is a duplicate concurrent request for the same api.
         only one request can acquire the lock for given expiry timeout , to alter this default behaviour and for
         another api to acquire the lock after first api has released but ttl is not finished ,
         release the lock from first api
         """
        Cache.get_instance().set(self.cache_key, self.api_run_id, nx=True, expiry_in_seconds=self.expiry_in_seconds)
        return Cache.get_instance().get(self.cache_key) == self.api_run_id

    def release_lock_for_api(self):
        from data_adapter.redis import Cache

        """release the lock if you want to allow the request to proceed even before lock is expired
        only api that acquired the lock can release the lock (hence checking api_run_id)"""
        if Cache.get_instance().get(self.cache_key) == self.api_run_id:
            Cache.get_instance().delete(self.cache_key)
        else:
            logger.error(extra=context_log_meta.get(),
                         msg="release_lock_for_api: api_run_id does not match with the one in cache")
