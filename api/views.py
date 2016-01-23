from django.shortcuts import (
    render, render_to_response, RequestContext, HttpResponseRedirect,
    get_object_or_404, render, Http404, HttpResponse
)
#from system.decorators import simpleauth
from mredphone.decorators import simpleauth
import zlib

@simpleauth
def gcm(request):
    if request.method == "DELETE":
        pass
    if request.method == "PUT":
        pass
    if request.method == "GET":
        pass
    return HttpResponse()

@simpleauth
def token(request, phone, id, key):
    if request.method == "DELETE":
        pass
    if request.method == "PUT":
        pass
    if request.method == "GET":
        pass
    return HttpResponse()
