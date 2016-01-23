#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# TODO: Make an app arch like the django has

import re
import socket

from http.request import Request
from datetime import datetime, timedelta
from urls import urlpatterns
from http.response import Http404

class Application:
    def __init__(self, *args):
        self.session_manager = None
        self.urls = {}
        self.load_urls(args)

    def get_url(self, request):
        path = request.META["PATH_INFO"]
        for pattern in self.urls:
            if re.match(pattern, path):
                d = re.search(pattern, path).groupdict()
                return self.urls[pattern](request, **d)
        return Http404()

    def load_urls(self, urls):
        if len(urls) < 1: raise AttributeError("Must have at least one url")
        for url in urls:
            if type(url) is not tuple:
                raise AttributeError("Must be a tuple")
            if len(url) != 2:
                raise AttributeError("Must be a pair of url and function")
            if not hasattr(url[1], '__call__'):
                raise AttributeError("Must be a function")
            r = re.compile(url[0],re.DOTALL|re.IGNORECASE)
            self.urls.update({url[0]:url[1]})

    def set_context(self, request, connection):
        request.session_manager = self.session_manager
        request.connection = connection

    def __call__(self, data, connection):
        request	= Request(data)
        if request.is_valid():
            self.set_context(request, connection)
            response = self.get_url(request)
            try:
                connection.write(response.serialize())
            except AttributeError:
                pass
            if not response.keep_alive:
                connection.close()
        else:
            connection.close()
