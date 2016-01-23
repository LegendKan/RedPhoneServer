from hashlib import sha1
from django.conf import settings
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponse, HttpResponseBase
from system.models import Account
from base64 import b64decode
import json

class Http401(HttpResponse):
    status_code = 401
    def __init__(self, *args, **kwargs):
        super(Http401, self).__init__(*args, **kwargs)
        self["WWW-Authenticate"] = 'Basic realm="Unauthorized"'

class Http403(HttpResponse):
    status_code = 403

def get_typetoken(text):
    return text.split(" ")

def get_loginpass(token):
    return b64decode(token).split(":")

def get_loginpassc(token):
    return b64decode(token).split(":")

def get_account(number):
    try:
        return Account.objects.get(number=number)
    except Account.DoesNotExist:
        return None

def simpleauth(func):
    def f(request, *args, **kwargs):
        auth = request.META.get("HTTP_AUTHORIZATION") 
        if auth:
            type, token = get_typetoken(auth)
            if type.lower() == "basic":
                number, passw = get_loginpass(token)
                account = get_account(number)
                if account and account.check_passw(passw):
                    return func(request, *args, **kwargs)
            if type.lower() == "otp":
                """
                    Here's the thing!
                    Do i need to save a client's passw to a base?
                    If i don't than how a can decode "passw,count" back ?
                """
                number, passw, counter = get_loginpassc(token)
                account = get_account(number)
                if account and account.check_passw_o(passw):
                    kwargs.update({"account":account})
                    return func(request, *args, **kwargs)
#                from hashlib import sha1
#                import hmac
#                # passw    : kryQiZQiVwEW8G2fzihYXVUqfiA=
#                # auth key : PNmzh02hcJ+PyYkaSeEIt82d
#                # Hguk+Wy6lj7rNkstlhV22vCtNy7gyi29zvCOl8lyCKSG5moawfQqGIukjalItiYZKRvweA==
#                hashed = hmac.new('PNmzh02hcJ+PyYkaSeEIt82d', counter, sha1)
#
#                #print 
#                #print "passw:", b64decode(passw).encode("hex")
#                #hashed = hmac.new('PNmzh02hcJ+PyYkaSeEIt82d', counter, sha1)
#                #print "hashed:", hashed.digest().encode("base64")
#                #print sha1('1562766083'+passw+counter).hexdigest().encode("base64")
            return Http403()
        return Http401()
    return f

"""
{
  u'identityKey': u'Bcz6oAEpTIfnNYad3OXWJbQdI2GVjCcmEyVH11dBFcMD', 
  u'number': u'+380938839815', 
  u'devices': [
    {
      u'authToken': u'0172a15f3da35491f6ccb050de80635ab47fbe5f', 
      u'pushTimestamp': 1451162150080, 
      u'registrationId': 13571, 
      u'name': None, 
      u'fetchesMessages': True, 
      u'voipApnId': None, 
      u'gcmId': u'APA91bFxTm1gq_CgZIBXmUC9Vh46ZBxiqEsV7Tc-YXmSUMr0j80spr-fz7VtV4KR5ZTdDuin6T_UqTfnT_LLQqmPiB4XTQZ7M-zuFpcBx9C0gXb89_g8Af20Isydj-ETRNDEsjtmPqOz', 
      u'signalingKey': u'xepuIVpX9/P0GQA/iMaSRGrVKBWWfmzfH/kSY27E2u+NMrAvJRb87c6AgTbQBer5fmZzGw==', 
      u'signedPreKey': {
        u'publicKey': u'BUy8DD8c1QfrXbKcl/5Tc4IDPPrL3ijyyIc7mv3q+34t', 
        u'keyId': 12955939, 
        u'signature': u'fg01XV/p+wD+TyKln/QlXzMfQe+eB2dg83QI0wnqqdSQy33zcSncvScv8vKJ45anrl59iduT1BwO6bAwcxLKDg'
      }, 
      u'lastSeen': 1451174400000, 
      u'created': 1451162148671, 
      u'userAgent': u'OWA', 
      u'voice': True, 
      u'salt': u'1562766083', 
      u'id': 1, 
      u'apnId': None}]}
"""
