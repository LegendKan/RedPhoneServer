import simplejson as json

from mredphone.http.response import (
    Http200, Http404, HttpBusy, HttpDelete, HttpRing
)
from mredphone.decorators import simpleauth
from system.models import Account
from pushclient import send_call_push

@simpleauth
def new_session(request, device_id, number):
    responder = Account.objects.get(number=number)
    manager = request.session_manager
    session_id = manager.create_session(request.connection)
    send_call_push(
                   responder,
                   int(device_id),
                   request.account.number,
                   int(session_id),
                   relay_name="textserver",
                   relay_port=5569,
    )
    relay = json.dumps({
        "relayPort":5570,
        "sessionId":session_id,
        "serverName":"textserver",
        "version":0
    })
    return Http200(relay)

@simpleauth
def get_session(request, session_id):
    manager = request.session_manager
    session = manager.sessions.get(session_id)
    if session is None:
        return Http404()
    if request.method == "BUSY":
        manager.send_busy(request, session_id)
        return HttpBusy()
    if request.method == "DELETE":
        manager.close_session(request, session_id)
        return HttpDelete()
    if request.method == "RING":
        manager.set_responder(request, session_id)
        return HttpRing()
