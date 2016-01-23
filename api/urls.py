from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    #/api/v1/accounts/gcm/
    #/api/v1/accounts/token/
    url(r'^v1/accounts/apn', 'api.views.apn'),
    url(r'^v1/accounts/gcm', 'api.views.gcm'),
    url(r'^v1/accounts/token/(?P<phone>[+0-9]{13}):(?P<id>\d+):(?P<key>[a-z0-9]+)', 'api.views.token'),
    url(r'^v1/push/gcm',    'api.views.push'),
    url(r'v1/feedback/gcm', 'api.views.feedback'),
    url(r'v1/feedback/apn', 'api.views.feedback'),
]
