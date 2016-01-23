#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import re
import simplejson as json
class Request:

    """ Request:
        <verb> <resource> HTTP/1.0\r\n
        Authorization: [Basic|OTP] <authorization_string>\r\n
        Content-Length: <length>\r\n
        \r\n
        <content>

        verbs: GET, RING, DELETE, BUSY
    """
    def __init__(self, data):
        self.META = {
            'REQUEST_METHOD':None,
            'SERVER_PROTOCOL':None,
            'REMOTE_ADDR':None,
            'CONTENT_LENGTH':None,
            'PATH_INFO':None,
            'HTTP_AUTHORIZATION':None,
        }
        self.method = None
        self.content = None
        self.data = data
        self.parse(self.data)
        self.session_manager = None
        self.connection = None

    def __repr__(self):
        text = {}
        text.update(self.META)
        text.update({'content':self.content})
        return json.dumps(self.META)

    def is_valid(self):
        if (self.META.get('REQUEST_METHOD') and
            self.META.get('PATH_INFO') and
            self.META.get('HTTP_AUTHORIZATION')
        ):
            return True
        return False

    def serialize(self):
        http_response = (
            "%(method)s %(path)s %(proto)s"
            "\r\n"
        ) % {
            "proto":  self.META['SERVER_PROTOCOL'],
            "path":   self.META['PATH_INFO'],
            "method": self.method
        }
        http_response += "\r\n"
        return http_response

    def parse(self, data):
        r = re.compile(
            (
                "^(?P<method>(GET|RING|DELETE|BUSY)) +"
                "(?P<path>[/0-9a-zA-Z+]+) +"
                "(?P<proto>[\./HTP0-9]+)"
                "\r\n"
                "Authorization: "
                "(?P<auth>((OTP|Basic) +[a-zA-Z0-9=]+))\r\n"
                ".*$"
            ),
            re.DOTALL|re.IGNORECASE
        )
        if re.match(r, data):
            result = re.search(r, data).groupdict()
            self.META["REQUEST_METHOD"]     = result.get("method")
            self.META["PATH_INFO"]          = result.get("path")
            self.META["HTTP_AUTHORIZATION"] = result.get("auth")
            self.META["CONTENT_LENGTH"]     = result.get("content_len")
            self.META["SERVER_PROTOCOL"]    = result.get("proto")
            self.method                     = result.get("method")
            self.content                    = result.get("content")
