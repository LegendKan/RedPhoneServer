#! /usr/bin/env python
# -*- encoding: utf-8 -*-
from mredphone.views import new_session, get_session

urlpatterns = [
    (r'^/session/(?P<session_id>\d+)$', get_session),
    (r'^/session/(?P<device_id>\d+)/(?P<number>[+0-9]{13})$', new_session),
]

