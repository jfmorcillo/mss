# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
import xmlrpclib

class MSSBackend:

    def authenticate(self, username=None, password=None):
        print username
        print password
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                # user exists, password ok
                return user
            else:
                # user exists but password is wrong
                # check if my password has changed
                return self.mss_authenticate(username, password)
        except User.DoesNotExist:
            # user does not exist, create account
            return self.mss_authenticate(username, password)

    def mss_authenticate(self, username=None, password=None):
        conn = xmlrpclib.ServerProxy('http://localhost:7000')
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
