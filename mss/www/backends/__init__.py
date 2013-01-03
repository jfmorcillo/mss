# -*- coding: UTF-8 -*-
#
# (c) 2010 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Mandriva Server Setup
#
# MSS is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MSS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MSS; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

from django.contrib.auth.models import User
from mss.www.xmlrpc import XmlRpc
from httplib import HTTPSConnection
from lib.PHPUnserialize import PHPUnserialize
import urllib


xmlrpc = XmlRpc()

class MSSBackend:

    def authenticate(self, username=None, password=None):
        err, result = xmlrpc.call('authenticate', username, password)
        # password ok
        if err:
            return None
        if result:
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
            # no my connection
            profile = user.profile
            profile.families = ""
            profile.save()
            return user
        # bad password
        else:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class MyBackend:

    def authenticate(self, username=None, password=None):
        # my authentication
        host = "my.mandriva.com"
        url  = "/rest/authenticate.php?username=%s&password=%s&_f=php&return=userData" % \
            (urllib.quote(username), urllib.quote(password))
        # get user data
        conn = HTTPSConnection(host)
        conn.request("GET", url)
        r1 = conn.getresponse()
        # check return code
        if r1.status == 200:
            s_user_data = r1.read()
        else:
            return None
        # unserialize user data
        u = PHPUnserialize()
        user_data = u.unserialize(s_user_data)
        # check return code
        if user_data['code'] == 0:
            # user is a mandriva member
            try:
                # user exists
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                print "user not exist"
                # check if there is no other my account in DB
                if len(User.objects.exclude(username="root")) > 0:
                    print "plop"
                    return None
                # create a new user
                user = User(username=username)
                user.is_staff = False
                user.is_superuser = False
                user.first_name = user_data['data']['firstname']
                user.last_name = user_data['data']['lastname']
                user.email = user_data['data']['email']
                user.set_password(password)
                user.save()
            # add family info into profile
            profile = user.profile
            profile.families = ",".join([family for key, family in user_data['data']['families'].items()])
            profile.save()
            return user
        else:
            # not a mandriva member
            return None

        # wrong username/password
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
