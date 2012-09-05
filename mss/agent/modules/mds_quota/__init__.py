# -*- coding: UTF-8 -*-
#
# (c) 2010-2012 Mandriva, http://www.mandriva.com/
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

from subprocess import Popen, PIPE

def get_config_info():
    return ("setup-quota.sh", ['filesystems'])

def get_filesystems(module):
    """
    Return / and /home devices for quotas
    """
    mountpoints = []
    p = Popen(["mount | grep '/dev/sd' | awk '{ print $1 \":\" $3 }'"], 
              shell=True, stdin=PIPE, stdout=PIPE, close_fds=True)
    for line in p.stdout:
        if line.strip().split('/').pop() in ['', 'home']:
            mountpoints.append(line.strip())

    return mountpoints
