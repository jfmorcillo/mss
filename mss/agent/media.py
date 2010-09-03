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

import urllib

class Media:

    def __init__(self, name, verbose_name, urls, auth=None, proto="https", mode="default"):
        self.name = name
        self.verbose_name = verbose_name
        self.auth = auth
        self.urls = urls
        self.proto = proto
        self.mode = mode
        
    def need_auth(self):
        if self.auth:
            return True
        else:
            return False
            
    def get_commands(self, login=None, password=None):
    
        commands = []    
        self.options = []
        
        if self.mode == "distrib":
            self.options.append('--distrib')
        elif self.mode == "updates":
            self.options.append('--updates')
        elif self.mode == "distrib_updates":
            self.options.append('--updates')            
            self.options.append('--distrib')
        else:
            self.options.append(self.name)
            
        for url in self.urls:
            if login and password:
                command = ['urpmi.addmedia'] + self.options + [ self.proto+"://"+urllib.quote(login)+":"+password+"@"+url ]
            else:
                command = ['urpmi.addmedia'] + self.options + [ self.proto+"://"+url ]
            commands.append(command)
            
        return commands
