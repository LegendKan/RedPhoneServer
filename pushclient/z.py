#! /usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import sys
from django import setup
os.environ['DJANGO_SETTINGS_MODULE'] = 'redphone.settings'
from system.models import Account
setup()

#for a in Account.objects.all():
#    print a.number, a.id, a.data
#quit()

import zlib
import simplejson as json

number = "+380938839815"
account = Account.objects.get(number=number)
deviceId = 1
device = account.get_device(deviceId)
gcmId = device.get("gcmId")
signalingKey = device.get("signalingKey")
print number, deviceId, gcmId

from base64 import b64decode, b64encode
import CompressedInitiateSignal_pb2
s = CompressedInitiateSignal_pb2.CompressedInitiateSignal()
s.initiator = "+380637250526"
s.sessionId = 1
s.port = 5570
s.serverName = "textserver"
s.version = 0

text = s.SerializeToString()

def sign_request(raw, key):
    from hashlib import sha1
    import hmac

    hashed = hmac.new(key, raw, sha1)

    return hashed.digest()

from Crypto.Cipher import AES
password = b64decode(signalingKey)
mac_key = password[16:36]

BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s : s[0:-ord(s[-1])]
# encrypt
cipher_key = password[:16]
IV = 16 * '\x00'
text = pad(text)
cipher = AES.new(cipher_key, AES.MODE_CBC, IV)
ciphertext = cipher.encrypt(text)
# dectypt
#decryptor = AES.new(key, mode, IV=IV)
#plain = decryptor.decrypt(ciphertext)

#pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
#unpad = lambda s : s[0:-ord(s[-1])]

message = "\x00"+IV+ciphertext
message += sign_request(message, mac_key)[10:]
message = b64encode(message)
print message

data = {
	"gcmId":gcmId,
	"number":number,
	"deviceId":deviceId,
	"message":message,
	"receipt":False,
	"notification":False,
	"redphone":False,
	"call":True
}
text = json.dumps(data)
gzip_compress = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)
data = gzip_compress.compress(text) + gzip_compress.flush()

from ensignal import PushClient
pc = PushClient("192.168.2.7", "8080", "123", "123")
print pc.send("PUT", "/api/v1/push/gcm", data)


# 70 | +380637250526 | {"number":"+380637250526","devices":[{"id":1,"name":null,"authToken":"7876b341b712b50b9aa0c2f9fb03bbd9a7a1c464","salt":"51602459","signalingKey":"dqj66o1LawcCdIkWAWkCTIgQSAbNfSGAC3aDtN5mxmh8qOtouQ8hGJmsnAYXF2se+uCP/A==",
    #"gcmId":"APA91bHei1ppcX-y0BcYwQLn0qthhAJQtr2tVv7z5elCsHqOoZMKE6DXK26HzKZ14Eub0TQt9ydT9BzLKGVLG_XjUPYtJLb1eC8h9NDLKyLggfXotF-OMQjEtDBDfE7jFUww8XHgNOfu","apnId":null,"voipApnId":null,"pushTimestamp":1451316614101,"fetchesMessages":true,"registrationId":10754,"signedPreKey":{"keyId":5943239,"publicKey":"Bboi0iYlLlq+Hx0TXuUQguuQZx0XqR4WgsvrtRfmN3Zd","signature":"X5S5DUA1AKUGprtpOOsMp3RcB/Zh1oQNtamSmgP2IgaW4av4SS/qnUiXuY3rWy7Fp8b0xDNUrSYks23k6p8hjQ"},"lastSeen":1451952000000,"created":1451316612693,"voice":true,"userAgent":"OWA"}],"identityKey":"BUdmyIfbA7nCNlKsPk4TKDqF1rR7SvCP3Yf0UUy0bFsf"}
# 71 | +380938839815 | {"number":"+380938839815","devices":[{"id":1,"name":null,"authToken":"57012b2654d8d0a8e1f2770cbb48991102c0cc6e","salt":"1050183115","signalingKey":"N0jhh7BbK8t52R7Kx8c2qKz3hRGWhwzwrSs8+1gHDfgXBXmdO/FUYMLuMxXOtUpHDh+Ynw==",
    #"gcmId":"APA91bEfvZsOmtTdHzaHKLKdL2xYbMwKPWYUnHgrkggrbUx3gDuGgJbLzsrp2uuLSmrmZtIdG3u_YCADrYBmt9cZTAzyyREwrBsN4PUkCif6c9_rI3VgpaVwkZIOccCL0bfIcVLc1sOY","apnId":null,"voipApnId":null,"pushTimestamp":1451325019392,"fetchesMessages":true,"registrationId":4475,"signedPreKey":{"keyId":16337459,"publicKey":"Bae8SR71qQBHp2UOxuNwbbBHyiddwdD2qlfR8EEzDCUw","signature":"hAYhKFxrGF4AUu15v9jNq7pqQzKVZ635lupS+/4M5uu3iULimiqI1YpGkQBequEZD5h52HvmbCcjjE+GkDnjhg"},"lastSeen":1452038400000,"created":1451325017978,"voice":true,"userAgent":"OWA"}],"identityKey":"BQHLVnMk75T+nAHa5yIkgMWQTjWP/dbmhwAMFxs0jWQw"}

   #{"gcmId":"APA91bHei1ppcX-y0BcYwQLn0qthhAJQtr2tVv7z5elCsHqOoZMKE6DXK26HzKZ14Eub0TQt9ydT9BzLKGVLG_XjUPYtJLb1eC8h9NDLKyLggfXotF-OMQjEtDBDfE7jFUww8XHgNOfu","number":"+380637250526","deviceId":1,"message":"","receipt":false,"notification":true}

#{"gcmId":"APA91bEfvZsOmtTdHzaHKLKdL2xYbMwKPWYUnHgrkggrbUx3gDuGgJbLzsrp2uuLSmrmZtIdG3u_YCADrYBmt9cZTAzyyREwrBsN4PUkCif6c9_rI3VgpaVwkZIOccCL0bfIcVLc1sOY",
#       "number":"+380938839815","deviceId":1,"message":"","call":""}
#{"gcmId":"APA91bEfvZsOmtTdHzaHKLKdL2xYbMwKPWYUnHgrkggrbUx3gDuGgJbLzsrp2uuLSmrmZtIdG3u_YCADrYBmt9cZTAzyyREwrBsN4PUkCif6c9_rI3VgpaVwkZIOccCL0bfIcVLc1sOY",
#       "number":"+380938839815","deviceId":1,"message":"","receipt":true,"notification":true,"redphone":true,"call":true}

