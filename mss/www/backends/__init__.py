# -*- coding: UTF-8 -*-
#
# (c) 2010-2013 Mandriva, http://www.mandriva.com/
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
from mss.lib.xmlrpc import XmlRpc


xmlrpc = XmlRpc()

class MSSBackend:

    def authenticate(self, username=None, password=None):
        err, result = xmlrpc.call('authenticate', username, password)
        if err:
            return None
        # password ok
        if result:
            try:
                # user exists so, we update the password
                user = User.objects.get(username=username)
                user.set_password(password)
                user.save()
            except User.DoesNotExist:
                # check if there is no other my account in DB
                if not username == "root" and len(User.objects.exclude(username="root")) > 0:
                    return None
                # create a new django user
                user = User(username=username)
                user.is_staff = False
                user.is_superuser = False
                if username == 'root':
                    user.email = 'root@localhost'
                else:
                    user.email = username
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
