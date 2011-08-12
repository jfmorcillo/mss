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

import xmlrpclib
from socket import error as socket_error
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


class XmlRpc:
    """ Class to handle the xmlrpc calls """

    def __init__(self):
        self.conn = xmlrpclib.ServerProxy('http://localhost:8001')

    def call(self, method_name, *args):
        method = getattr(self.conn, method_name)
        try:
            return [False, method(*args)]
        except socket_error, err:
            return [HttpResponseRedirect(reverse('error', args=[err[0]])), False]

# xmlrpclib.Fault, xmlrpclib.ProtocolError, xmlrpclib.ResponseError)
