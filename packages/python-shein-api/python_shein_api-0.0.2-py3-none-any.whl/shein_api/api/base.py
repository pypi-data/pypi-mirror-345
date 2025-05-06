# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from shein_api.base.api_response import ApiResponse


class BaseAPI(object):
    """ Shein API base class """

    def __init__(self, client=None):
        self._client = client

    def _request(self, data: dict = None, params: dict = None) -> ApiResponse:

        return self._client.request(data=data, params=params)
