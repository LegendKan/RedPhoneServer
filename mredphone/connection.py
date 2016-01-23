#! /usr/bin/env python
# -*- encoding: utf-8 -*-
import ssl
import socket
import select
from datetime import datetime

class Connection(ssl.SSLSocket):

    def __init__(self, sock=None, addr=None,
        """ Connection(unsecure_socket, addr, certfile, keyfile) """
                 certfile,
                 keyfile):
        sock.setblocking(0)
        super(Connection, self).__init__(
            sock,
            server_side=True,
            certfile=certfile,
            keyfile=keyfile,
            do_handshake_on_connect=False
        )
        self.fileno = None
        self.session = None
        self.responder = None
        self.addr = addr
        self.do_handshake()

    def do_handshake(self):
        while True:
            try:
                super(Connection, self).do_handshake()
                self.fileno = self._sock.fileno
                break
            except ssl.SSLError, err:
                if err.args[0] == ssl.SSL_ERROR_WANT_READ:
                    select.select([self._sock], [], [])
                elif err.args[0] == ssl.SSL_ERROR_WANT_WRITE:
                    select.select([], [self._sock], [])
            else:
                raise

    def create_session(self):
        add_num = sum(
            [int(x) for x in self.addr[0].split(".")]
        ) + int(self.addr[1])

        delta = datetime.now() - datetime(1970,1,1)
        try:
            id = int(delta.total_seconds())
        except AttributeError:
            id = int(delta.days * 86400 + delta.seconds)

        self.session = "%s" % (id + add_num)
        return self.session

    def read(self, size=1024):
        try:
            return self._sslobj.read(size)
        except AttributeError:
            raise

