#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# TODO: Make an app arch like the django has
from base64 import b64decode
from system.models import Account
from http.response import Http401, Http404

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
            type, token = auth.split(" ")
            if type.lower() == "basic":
                number, passw = get_loginpass(token)
                account = get_account(number)
                if account and account.check_passw(passw):
                    request.account = account
                    return func(request, *args, **kwargs)
            if type.lower() == "otp":
                number, passw, c = get_loginpassc(token)
                account = get_account(number)
                if account and account.check_passw_o(passw):
                    request.account = account 
                    return func(request, *args, **kwargs)
            return Http404()
        return Http401()
    return f
