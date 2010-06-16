# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
import xmlrpclib

class MSSBackend:

    def authenticate(self, username=None, password=None):
        conn = xmlrpclib.ServerProxy('http://localhost:7001')
        auth = conn.authenticate(username, password)
        # password ok
        if auth:
            try:
                # user exists so, we update the password
                user = User.objects.get(username=username)
                user.set_password(password)
                user.save()
            except User.DoesNotExist:
                # create a new django user
                user = User(username=username)
                user.is_staff = False
                user.is_superuser = False
                user.email = 'root@localhost'
                user.set_password(password)
                user.save()
            return user
        # bad password
        else:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
