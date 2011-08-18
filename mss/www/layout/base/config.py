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

from django.utils.translation import ugettext as _
from mss.www.wizard.config import ConfigManager

config = ConfigManager()

config.add_section({'id': 'mds', 'name': _('Mandriva Directory Server'),
    'icon': 'base/section_mds.png', 'desc': _('MDS is an enterprise directory platform based on LDAP designed to manage identities, and various network services commonly used.<br/><br/>In addition, MDS is controlled through a modern and friendly web interface.<br /><br />For an overview of MDS, visit the <a href="http://mds.mandriva.org/">project website</a>.'),
    'conf': {'class': 'block-2 block-clear'}})

config.add_bundle("mds", {'id': 'mds', 'name': _('Mandriva Directory Server'),
    'icon': 'base/bundle_authentication.png', 'desc': _('Required base components'),
    'conf': {'class': 'block-1'},'modules': ["mds_mmc"]})

config.add_bundle("mds", {'id': 'fs', 'name': _('File server modules'),
    'icon': 'base/bundle_fileserver.png', 'desc': _('SAMBA, Cups and quota support'),
    'conf': {'class': 'block-2 block-clear'}, 'modules': ["mds_smb", "mds_quota", "mds_cups"]})

config.add_bundle("mds", {'id': 'mail', 'name': _('Mail modules'),
    'icon': 'base/bundle_mail.png', 'desc': _('SMTP, IMAP server and other tools'),
    'conf': {'class': 'block-2'}, 'modules': ["mds_mail", "mds_webmail"]})

config.add_bundle("mds", {'id': 'net', 'name': _('Network modules'),
    'icon': 'base/bundle_network.png', 'desc': _('Network managing tools'),
    'modules': ["mds_dns", "mds_dhcp"], 'conf': {'class': 'block-2 block-clear'}})

config.add_bundle("mds", {'id': 'other', 'name': _('Other modules'),
    'icon': 'base/section_advanced.png', 'desc': _('Various MDS modules'),
    'conf': {'class': 'block-2'}, 'modules': ["mds_audit", "mds_bulkimport", "mds_kerberos"]})

config.add_section({'id': 'pulse2', 'name': _('Pulse 2 - Coming soon'),
    'icon': 'base/section_pulse2.png', 'desc': _('Pulse 2 is an Open Source tool that simplifies application deployment, inventory, and maintenance of an IT network.<br />It has been designed to handle from a few computers on a single site to 100 000+ computers spread on many sites.<br /><br />For more information on Pulse 2, visit the <a href="http://pulse2.mandriva.org/">project website</a>.'),
    'conf': {'class': 'block-2 disabled'}})

config.add_section({'id': 'advanced', 'name': _('Server services and tools'),
    'icon': 'base/section_advanced.png', 'desc': _('Install basic server stacks like DHCP, OpenLDAP or VPN software.'),
    'conf': {'class': 'block-2'}})

config.add_bundle("advanced", {'id': 'net', 'name': _('Network'),'icon': 'base/bundle_network.png',
    'desc': _('Network managing tools'), 'modules': ["dns", "dhcp"],
    'conf': {'class': 'block-2 block-clear'}})

config.add_bundle("advanced", {'id': 'lamp', 'name': _('LAMP server'), 'icon': 'base/bundle_lamp.png',
    'desc': _('Toolkit for dynamic web site hosting'), 'modules': ["lamp_server", "lamp_dev"],
    'conf': {'class': 'block-2'}})

config.add_bundle("advanced", {'id': 'fs', 'name': _('Printing and file server'), 'icon': 'base/bundle_fileserver.png',
    'desc': _('SAMBA, Cups and NFS servers.'), 'modules': ["samba", "cups", "nfs", "proftpd"],
    'conf': {'class': 'block-2 block-clear'}})

config.add_bundle("advanced", {'id': 'db', 'name': _('Databases'), 'icon': 'base/bundle_database.png',
    'desc': _('Relational databases'), 'modules': ["mysql", "mysqlmax", "postgresql", "sqlite"],
    'conf': {'class': 'block-2'}})

config.add_bundle("advanced", {'id': 'backup', 'name': _('Backup Tools'), 'icon': 'base/bundle_backup.png',
    'desc': _('Backup Server'), 'modules': ["bacula_director", "bacula_storage", "bacula_file"],
    'conf': {'class': 'block-2 block-clear'}})

config.add_bundle("advanced", {'id': 'mail', 'name': _('Mail server'), 'icon': 'base/bundle_mail.png',
    'desc': _('Mail server with POP/IMAP and Webmail access'),
    'modules': ["postfix", "spam", "cyrus", "dovecot", "courierimap", "sympa", "roundcube"],
    'conf': {'class': 'block-2'}})

config.add_bundle("advanced", {'id': 'auth', 'name': _('Authentication'),'icon': 'base/bundle_authentication.png',
    'desc': _('Tools for managing identities'), 'modules': ["openldap", "kerberos", "openldap_kerberos"],
    'conf': {'class': 'block-2 block-clear'}})
