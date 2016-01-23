from django.db import models
from hashlib import sha1

class Account(models.Model):
    id     = models.BigIntegerField(primary_key=True, null=False)
    number = models.CharField(max_length=255, null=False)
    data = models.TextField(null=False)
    class Meta:
        db_table = "accounts"

    def get_device(self, id):
        for device in self.data.get("devices", []):
            if device.get("id") == id:
                return device
        return None

    def check_passw_o(self, passw):
        # temporarily hack
        # dunno how to solve phone:(passw:counter):counter
        # Do we need to save passw O_o
        return True

    def check_passw(self, passw):
        for device in self.data.get("devices", []):
            token = device.get("authToken","")
            salt  = device.get("salt", "")
            if token == sha1(salt+passw).hexdigest():
                return True
        return False
