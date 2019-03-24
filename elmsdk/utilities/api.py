# -*- coding: utf-8 -
#
import requests
from requests.exceptions import ConnectionError
from elmsdk.configuration import settings
from .base_functions import ElmwareError
import time
import json


class ElmwareRequestError(ElmwareError):
    """
    Exceptions raised when requests fail
    """
    pass



class APIRequests:
    """
    Module for making requests to the api
    """

    def __init__(self, instance_key, dev_mode=False):
        self.instance_key = instance_key
        self.dev_mode = dev_mode
        self.dev_key = 'dev' if self.dev_mode else 'app'


    def build_url(self, target, url_override=False):
        """
        private method - create url from target
        """
        url = settings.API_ROOT
        if url_override:
            url = url_override
        return "{0}/{1}Api/{2}/{3}/".format(url, self.dev_key, self.instance_key, target )

    @staticmethod
    def parse_response(resp):
        """
        Check response from server for errors, and returned parsed json from response
        """
        if resp.status_code == 503:
            raise ConnectionError("Server Busy")
        try:
            data = resp.json()
        except json.decoder.JSONDecodeError:
            raise ElmwareRequestError('Invalid Server Response')
        if resp.status_code > 200:
            raise ElmwareRequestError(data['message'])
        return data

    def get_request_inner(self, target, args, retry_depth=0, url_override=False):
        """
        private method - perform the outbound get request and handle connection errors
        """
        if retry_depth >= settings.MAX_CONNECTIVITY_RETRY:
            raise ElmwareRequestError("Unable to connect to the server.")
        try:
            return self.parse_response(requests.get(self.build_url(target, url_override=url_override), params=args, headers=settings.GET_HEADERS))
        except (ConnectionError, ConnectionResetError):
            time.sleep(settings.API_RETRY_DELAY)
            return self.get_request_inner(target, args, url_override=url_override, retry_depth=retry_depth + 1)

    def post_request_inner(self, target, payload, retry_depth=0, url_override=False):
        """
        private method - perform the outbound get request and handle connection errors
        """
        if retry_depth >= settings.MAX_CONNECTIVITY_RETRY:
            raise ElmwareRequestError("Unable to connect to the server.")
        try:
            return self.parse_response(requests.post(self.build_url(target, url_override=url_override), json=payload, headers=settings.POST_HEADERS))
        except (ConnectionError, ConnectionResetError):
            time.sleep(settings.API_RETRY_DELAY)
            return self.post_request_inner(target, payload, url_override=url_override, retry_depth=retry_depth + 1)
        except TypeError:
            raise ElmwareRequestError("Payload not serializable.")


    @classmethod
    def get_request(cls, target, instance_key, dev_mode=False, args={}, url_override=False):
        """
        public class method - make a get request to the api
        """
        operator = cls(instance_key,  dev_mode=dev_mode)
        return operator.get_request_inner(target, args, url_override=url_override)


    @classmethod
    def post_request(cls, target, instance_key, dev_mode=False, data={}, url_override=False):
        """
        public class method - make a get request to the api
        """
        operator = cls(instance_key,  dev_mode=dev_mode)
        return operator.post_request_inner(target, data, url_override=url_override)
