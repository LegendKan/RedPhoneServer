#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

DJANGO_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def daemon(iport):
    import tornado.wsgi
    import tornado.ioloop
    import tornado.httpserver

    sys.path.insert(0, DJANGO_ROOT_DIR)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'redphone.settings'
    import django.core.wsgi
    application = django.core.wsgi.get_wsgi_application()

    # tornado
    container = tornado.wsgi.WSGIContainer(application)
    http_server = tornado.httpserver.HTTPServer(container)
    http_server.listen(iport, "0.0.0.0")
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    if len(sys.argv[1]) < 2:
        quit()
    daemon(int(sys.argv[1]))


