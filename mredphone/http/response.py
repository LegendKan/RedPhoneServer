#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import re

class Response:

    """
        HTTP/1.0 <response_code> <response_string>\r\n
        Content-Length: <length>\r\n
        \r\n
        <content>
    """
    def __init__(self, content=""):
        self.proto = "HTTP/1.0"
        self.headers = {}
        self.content = content
        self.content_len = len(content)

    def serialize(self):
        http_response = (
            "%(proto)s %(status_code)s %(status_text)s"
            "\r\n"
        ) % {
            "proto": self.proto,
            "status_code": self.status_code,
            "status_text": self.status_text
        }
        for header in self.headers:
            http_response += "%s: %s\r\n" % (
                header, self.headers[header]
            )
        http_response += "Content-Length: %s\r\n\r\n" % (
            self.content_len
        )
        if self.content:
            http_response += self.content
        http_response += "\r\n"
        return http_response

class Http200(Response):
    """ All are ok """
    status_code = 200
    status_text = "OK"
    keep_alive = True

class Http404(Response):
    """ No such user or session """
    status_code = 404
    status_text = "Not Found"
    keep_alive = False

class Http403(Response):
    """ Forbidden """
    status_code = 200
    status_text = "Forbidden"
    keep_alive = False

class Http401(Response):
    """ Login or Password is incorrect """
    status_code = 401
    status_text = "Unauthorized"
    keep_alive = False
    def __init__(self, *argv, **kargv):
        super(self, Http401).__init__(*argv, **kargv)
        self.headers.update({"WWW-Authenticate":'Basic realm="Unauthorized"'})

class HttpBusy(Response):
    """ BUSY """
    status_code = 200
    status_text = "OK"
    keep_alive = False

class HttpDelete(Response):
    """ DELETE """
    status_code = 200
    status_text = "OK"
    keep_alive = False

class HttpRing(Response):
    """ RING """
    status_code = 200
    status_text = "OK"
    keep_alive = True
