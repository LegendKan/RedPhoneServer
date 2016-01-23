import string
import zlib
import httplib
import random
import simplejson as json
import hmac
import hashlib
from Crypto.Cipher import AES
from CompressedInitiateSignal_pb2 import (
    CompressedInitiateSignal as CIS
)
from base64 import b64encode, b64decode
from django.conf import settings
from system.models import Account

class PushClient:

    def __init__(self, server, port, login, passw):
        self.server = server
        self.port = port
        self.headers = {
            "Content-type": "application/json",
            "Authorization": "Basic " + b64encode(login+":"+passw),
            "User-Agent": "whisper-server (whisper-server)",
            "Content-Encoding": "gzip"
        }

    def pack_data(self, text):
        gzip_compress = zlib.compressobj(
            9, zlib.DEFLATED, zlib.MAX_WBITS | 16
        )
        return gzip_compress.compress(text) + gzip_compress.flush()

    def send(self, method, uri, data):
        gzip_data = self.pack_data(data)
        conn = httplib.HTTPConnection(
            self.server,
            self.port,
            timeout = 1
        )
        conn.request(
            method,
            uri,
            gzip_data,
            self.headers
        )
        response = conn.getresponse()
        conn.close()
        if response.status not in [200,204]:
            raise IOError(response.status)
        return response.status

class CallSignal:

    def __init__(self):
        self.block_size  = 16

    def create_iv(self):
        return "".join(
            random.SystemRandom().choice(
                string.ascii_uppercase + string.digits
            ) for _ in range(16)
        )

    def pad_text(self, text, BS=None):
        """ add \x00 to the end of the string """
        if BS is None: BS = 16
        return text + (BS - len(text) % BS) * chr(BS - len(text) % BS)

    def unpad_text(self, text):
        """ delete \x00 from the end of the string """
        return text[0:-ord(text[-1])]

    def get_mac_key(self, signaling_key):
        return b64decode(signaling_key)[16:36]

    def get_cipher_key(self, signaling_key):
        return b64decode(signaling_key)[:16]

    def sign_request(self, text, key):
        """ must be truncated to 80 bit """
        return hmac.new(key, text, hashlib.sha1).digest()[10:]

    def __call__(self, **kargv):
        cis = CIS()
        cis.version = 0
        cis.initiator = kargv["number"]
        cis.sessionId = kargv["session_id"]
        cis.port = kargv["relay_port"]
        cis.serverName = kargv["relay_name"]
        signaling_key = kargv["signaling_key"]
        return self.serialize(cis, signaling_key)

    def serialize(self, cis, signaling_key):
        signaling_key = signaling_key #!!!!!
        iv = self.create_iv()
        text = self.pad_text(cis.SerializeToString())
        cipher_key = self.get_cipher_key(signaling_key)
        mac_key = self.get_mac_key(signaling_key)
        cipher = AES.new(cipher_key, AES.MODE_CBC, iv)
        cipher_text = cipher.encrypt(text)
        version = '\x00'
        message = version + iv + cipher_text
        message += self.sign_request(message, mac_key)
        message = b64encode(message)
        return message

call_signal = CallSignal()

# temporarily function
def send_call_push(
                   account, device_id,
                   number, session_id,
                   relay_name, relay_port):
    device = account.get_device(device_id)
    gcm_id = device.get("gcmId")
    signaling_key = device.get("signalingKey")
    message = call_signal(
        number=number,
        session_id=session_id,
        relay_port=relay_port,
        relay_name=relay_name,
        signaling_key=signaling_key
    )
    data = json.dumps({
        "gcmId": gcm_id,
        "number": number,
        "deviceId": "1",
        "message": message,
        "call":True
    })
    # put it ti the settings file
    pc = PushClient("192.168.2.7", "8080", "123", "123")
    pc.send("PUT", "/api/v1/push/gcm", data)

if __name__ == "__main__":
    message = call_signal(
        number="+123456789012", # number of initiator
        session_id="0",         # session id
        relay_port="8080",      # port of relay server
        relay_name="relay",     # subdomain name of the relay
        singaling_key="..."     # signaling key of the responder
    )
    data = {
        "gcmId":"...",          # responder's gcmId
        "number":"+09876543212",# responder's phone number
        "deviceId":"1",         # device id of the responder
        "message":message,      # packed message(in our case it's call_signal)
                                # I think bellow we have the types of notification
        "receipt":False,        # unknown
        "notification":False,   # text message notification 
        "redphone":False,       # unknown | compatibility with old redphone ?
        "call":True             # call notification
    }
    pc = PushClient("192.168.10.10", "8080", "login", "passw")
    print pc.send("PUT", "/api/v1/push/gcm", data)
