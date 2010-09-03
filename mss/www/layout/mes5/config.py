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
from mss.www.wizard.config import Config

config = Config()

mds = { 
    'name': _('Mandriva Directory Server'), 
    'id': 'mds', 
    'icon': 'mes5/section_mds.png',
    'desc': _('MDS is an enterprise directory platform based on LDAP designed to manage identities, and various network services commonly used.<br/><br/>In addition, MDS is controlled through a modern and friendly web interface.<br /><br />For an overview of MDS, visit the <a href="http://mds.mandriva.org/">project website</a>.'),
    'conf': {'class': 'block-2 block-clear'}
}
    
pulse2 = { 
    'name': _('Pulse 2 - Coming soon'), 
    'id': 'pulse2', 
    'icon': 'mes5/section_pulse2.png',
    'desc': _('Pulse 2 is an Open Source tool that simplifies application deployment, inventory, and maintenance of an IT network.<br />It has been designed to handle from a few computers on a single site to 100 000+ computers spread on many sites.<br /><br />For more information on Pulse 2, visit the <a href="http://pulse2.mandriva.org/">project website</a>.'),
    'conf': {'class': 'block-2 disabled'},
}

partners = { 
    'name': _('Partners'), 
    'id': 'partners', 
    'icon': 'mes5/section_partners.png',
    'desc': _('Several appliances from our partners.'),
    'conf': {'class': 'block-2 block-clear'},
}

advanced = { 
    'name': _('Server services and tools'), 
    'id': 'advanced', 
    'icon': 'mes5/section_advanced.png',
    'desc': _('Install basic server stacks like DHCP, OpenLDAP or VPN software.'),
    'conf': {'class': 'block-2'},
}

config.add_section(mds)
config.add_section(pulse2)
config.add_section(partners)
config.add_section(advanced)

mds = [
    {
        'id': '1',
        'name': _('Mandriva Directory Server'),
        'icon': 'mes5/bundle_authentication.png',
        'desc': _('Required base components'),
        'conf': {'class': 'block-1'},
        'modules': ["mds_mmc"],
    },
    {
        'id': '2',    
        'name': _('File server modules'),
        'icon': 'mes5/bundle_fileserver.png',
        'desc': _('SAMBA, Cups and quota support'),
        'conf': {'class': 'block-2 block-clear'},
        'modules': ["mds_smb", "mds_quota", "mds_cups"],
    },
    {
        'id': '3',    
        'name': _('Mail modules'),
        'icon': 'mes5/bundle_mail.png',
        'desc': _('SMTP, IMAP server and other tools'),
        'conf': {'class': 'block-2'},
        'modules': ["mds_mail", "mds_webmail"],
    },
    {
        'id': '4',    
        'name': _('Network modules'),
        'icon': 'mes5/bundle_network.png',
        'desc': _('Network managing tools'),
        'modules': ["mds_dns", "mds_dhcp"],
        'conf': {'class': 'block-2 block-clear'},
    },
    {
        'id': '5',    
        'name': _('Other modules'),
        'icon': 'mes5/section_advanced.png',
        'desc': _('Various MDS modules'),
        'conf': {'class': 'block-2'},
        'modules': ["mds_audit", "mds_bulkimport"],
    }        
]
config.add_modules("mds", mds)

advanced = [
    { 
        'id': '1',
        'name': _('Network'), 
        'icon': 'mes5/bundle_network.png',            
        'desc': _('Network managing tools'), 
        'modules': ["dns", "dhcp"],
        'conf': {'class': 'block-2 block-clear'},
    },
    {
        'id': '2',
        'name': _('LAMP server'),
        'icon': 'mes5/bundle_lamp.png',
        'desc': _('Toolkit for dynamic web site hosting'), 
        'modules': ["lamp_server", "lamp_dev"],
        'conf': {'class': 'block-2'},
    },
    {
        'id': '3', 
        'name': _('Printing and file server'),
        'icon': 'mes5/bundle_fileserver.png',
        'desc': _('SAMBA, Cups and NFS servers.'), 
        'modules': ["samba", "cups", "nfs", "proftpd"],
        'conf': {'class': 'block-2 block-clear'},
    },
    { 
        'id': '4',
        'name': _('Databases'),
        'icon': 'mes5/bundle_database.png',
        'desc': _('Relational databases'), 
        'modules': ["mysql", "mysqlmax", "postgresql", "sqlite"],
        'conf': {'class': 'block-2'},
    },
    {
        'id': '5',
        'name': _('Backup Tools'),
        'icon': 'mes5/bundle_backup.png',
        'desc': _('Backup Server'), 
        'modules': ["bacula_director", "bacula_storage", "bacula_file"],
        'conf': {'class': 'block-2 block-clear'},
    },        
    { 
        'id': '6',
        'name': _('Mail server'),
        'icon': 'mes5/bundle_mail.png',
        'desc': _('Mail server with POP/IMAP and Webmail access'), 
        'modules': ["postfix", "spam", "cyrus", "dovecot", "courierimap", "sympa", "roundcube"],
        'conf': {'class': 'block-2'},
    }, 
    {
        'id': '7',
        'name': _('Authentication'),
        'icon': 'mes5/bundle_authentication.png',
        'desc': _('Tools for managing identities'), 
        'modules': ["openldap", "kerberos", "openldap_kerberos"],
        'conf': {'class': 'block-2 block-clear'},
    },          
]
config.add_modules("advanced", advanced)

partners = [
    { 
        'id': '1',
        'name': _('eGroupware Suite'),
        'icon': 'mes5/bundle_egroupware.png',
        'desc': _('eGroupware is a enterprise ready groupware software for your network. It enables you to manage contacts, appointments, todos and many more for your whole business. eGroupware is a groupware server. It comes with a native web-interface which allowes to access your data from any platform all over the planet. Moreover you also have the choice to access the EGroupware server with your favorite groupware client (Kontact, Evolution, Outlook) and also with your mobile or PDA via SyncML.'), 
        'modules': ["egroupware"],
        'conf': {'class': 'block-2 block-clear'},
    },
    { 
        'id': '2',
        'name': _('Group-Office'),
        'icon': 'mes5/bundle_groupoffice.png',
        'desc': _('Take your office online. Share projects, calendars, files and e-mail online with co-workers and clients. Easy to use and fully customizable, Group-Office takes online collaboration to the next level.'), 
        'modules': ["groupoffice"],
        'conf': {'class': 'block-2'},
    },
    { 
        'id': '3',
        'name': _('Authentication Firewall Suite for Linux'),
        'icon': 'mes5/bundle_nufw.png',
        'desc': _('NuFW adds user-based filtering to Netfilter, the state of the art IP filtering layer from the Linux kernel. Its exclusive algorithm allows authenticated filtering even on multiuser computers'), 
        'modules': ["nufw"],
        'conf': {'class': 'block-2 block-clear'},
    },        
]
config.add_modules("partners", partners)
