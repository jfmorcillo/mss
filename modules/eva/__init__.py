# -*- coding: UTF-8 -*-
#
# (c) 2012 Mandriva, http://www.mandriva.com/
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

from mss.agent.managers.translation import TranslationManager
_ = TranslationManager().translate


def get_config_info():
    return ('setup-eva.sh', ["default_language", "password_eva"])


def valid_lic(lic):
    """Check that the license has been accepted"""
    if lic == "on":
        return None
    else:
        return _("You must accept the license", "eva")
