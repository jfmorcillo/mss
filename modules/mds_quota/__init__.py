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

import os
import psutil
from mss.agent.managers.translation import TranslationManager

_ = TranslationManager().translate


def get_config_info():
    return ("setup-quota.sh", ['filesystems'])


def _is_subdir(a, b):
    """Return True if 'b' is a sub directory of 'a'"""
    return os.path.commonprefix([a, b]) == a

def get_filesystems(module):
    """
    Return all devices for quotas
    """
    mountpoints = {}
    for part in psutil.disk_partitions(all=False):
        # Filter out any bind mounts
        if part.device in mountpoints:
            if _is_subdir(mountpoints[part.device], part.mountpoint):
                continue
        if part.fstype in ('ext3', 'ext4', 'xfs'):
            mountpoints[part.device] = part.mountpoint

    return ["%s:%s" % (dev, mntpnt) for dev, mntpnt in mountpoints.items()]


def validate_filesystems(filesystems):
    """
    Validate device name
    """
    for filesystem in filesystems:
        device = filesystem.split(':')[0]
        valid = False
        for part in psutil.disk_partitions(all=False):
            if device == part.device:
                valid = True
                break

        if not valid:
            return _("Device %s doesn't exists." % device, "mds_quota")

    return None
