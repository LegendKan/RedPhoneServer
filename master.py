#! /usr/bin/env python
# -*- encoding: utf-8 -*-
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'redphone.settings'
import ssl
import socket
import select
import threading
import time

from datetime import datetime

from mredphone.application import Application
from mredphone.connection import Connection
from mredphone.urls import urlpatterns as urls
from django.conf import settings

class RedphoneMaster(threading.Thread):
    """
        Main worker class extended from Thread.
        It works with connections.

        When a client rings or receiving a call
        the worker handles connection in to sessions.

        Whis daemon does not work relay job.
    """

    def __init__(self, application):
        threading.Thread.__init__(self)
        self.application = application
        self.application.session_manager = self
        self.temp = 0
        self.connections = []
        self.sessions = {}
        self.started = datetime.now()

    def handle_error_conn(self, connections):
        self.connections = [x for x in self.connections if x not in connections]

    def handle_connections(self):
        """ handles all connections and kills invalids """
        error_sockets = []
        r,w,e = select.select(
            self.connections,
            self.connections,
            self.connections,
            0
        )
        for conn in r:
            try:
                data = conn.read()
                self.application(data, conn)
            except (ssl.SSLError, AttributeError, socket.error):
                error_sockets.append(conn)
        if len(e) > 0:
            error_sockets += e
        if len(error_sockets):
            self.handle_error_conn(error_sockets)

    def run(self):
        while True:
            if len(self.connections) > 0:
                self.handle_connections()
            time.sleep(0.01)

    def create_session(self, connection):
        self.temp += 1
        id = "%i" % self.temp
        self.sessions.update({id:{
            "initiator":connection,
            "responder":None,
        }})
        connection.session = id
        return id

    def set_responder(self, request, session_id):
        session = self.sessions.get(session_id)
        responder = request.connection
        initiator = session["initiator"]
        #
        session["responder"] = responder
        #
        initiator.responder = responder
        responder.responder = initiator

    def close_session(self, request, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]
        #
        initiator = request.connection
        responder = initiator.responder
        #
        try:
            responder.write(request.serialize())
        except AttributeError:
            pass

    def add_connection(self, connection):
        self.connections.append(connection)

    def stop(self):
        self._Thread__stop()

if __name__ == "__main__":
    import django
    django.setup()
    from django.conf import settings
    try:
        bindsocket = socket.socket()
        bindsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        bindsocket.bind(('', 31337))
        bindsocket.listen(5)

        application = Application(*urls)
        redphone_master = RedphoneMaster(application)
        redphone_master.start()

        certfile = settings.CERTFILE
        keyfile = settings.KEYFILE

        while True:
            newsocket, addr = bindsocket.accept()
            connection = Connection(newsocket, addr, certfile, keyfile)
            redphone_master.add_connection(connection)
            time.sleep(0.1)

    except (KeyboardInterrupt):
        redphone_master.stop()
