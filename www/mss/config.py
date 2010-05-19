# -*- coding: UTF-8 -*-

from django.utils.translation import ugettext as _

SECTIONS = [
    { 
        'name': _('Mandriva Directory Server'), 
        'id': 'mds', 
        'icon': 'section_mds.png',
        'desc': _('MDS is an enterprise directory platform based on LDAP designed to manage identities, and various network services commonly used.<br/><br/>In addition, MDS is controlled through a modern and friendly web interface.<br /><br />For an overview of MDS, visit the <a href="http://mds.mandriva.org/">project website</a>.'),
        'conf': {'class': 'block-2'},
    },
    { 
        'name': _('Pulse 2'), 
        'id': 'pulse2', 
        'icon': 'section_pulse2.png',
        'desc': _('Pulse 2 is an Open Source tool that simplifies application deployment, inventory, and maintenance of an IT network.<br /><br />It has been designed to handle from a few computers on a single site to 100 000+ computers spread on many sites.<br /><br />For more information on Pulse 2, visit the <a href="http://pulse2.mandriva.org/">project website</a>.'),
        'conf': {'class': 'block-2 block-last'},
    },
    { 
        'name': _('Partners'), 
        'id': 'partners', 
        'icon': 'section_partners.png',
        'desc': _('Install basic server stacks like DHCP, OpenLDAP or VPN software.'),
        'conf': {'class': 'block-2 block-clear'},
    },    
    { 
        'name': _('Advanced'), 
        'id': 'advanced', 
        'icon': 'section_advanced.png',
        'desc': _('Install basic server stacks like DHCP, OpenLDAP or VPN software.'),
        'conf': {'class': 'block-2 block-last'},
    },
]

SECTIONS_MODULES = {
    'mds': [
        {
            'name': _('Mandriva Directory Server'),
            'icon': 'bundle_authentication.png',
            'desc': _('Required base components'),
            'modules': ["mds_mmc"],
            #'conf': {'required': True},
        },
        {
            'name': _('File server modules'),
            'icon': 'bundle_fileserver.png',
            'desc': _('Samba, Cups and quota support'),
            'conf': {'class': 'block-2'},
            'modules': ["mds_smb", "mds_quota", "mds_cups"],
        },
        {
            'name': _('Mail modules'),
            'icon': 'bundle_mail.png',
            'desc': _('SMTP, IMAP server and other tools'),
            'conf': {'class': 'block-2 block-last'},
            'modules': ["mds_mail", "mds_webmail"],
        },
        {
            'name': _('Network modules'),
            'icon': 'bundle_network.png',
            'desc': _('Network managing tools'),
            'modules': ["mds_dns", "mds_dhcp"],
            'conf': {'class': 'block-2 block-clear'},
        },
        {
            'name': _('Other modules'),
            'icon': 'section_advanced.png',
            'desc': _('Various MDS modules'),
            'conf': {'class': 'block-2 block-last'},
            'modules': ["mds_audit", "mds_bulkimport"],
        }        
    ],
    'advanced': [
        { 
            'name': _('Network'), 
            'icon': 'bundle_network.png',            
            'desc': _('Network managing tools'), 
            'modules': ["dns", "dhcp"],
            'conf': {'class': 'block-2'},
        },
        { 
            'name': _('Authentication'),
            'icon': 'bundle_authentication.png',
            'desc': _('Tools for managing identities'), 
            'modules': ["openldap"],
            'conf': {'class': 'block-2 block-last'},
        },
        { 
            'name': _('Databases'),
            'icon': 'bundle_authentication.png',
            'desc': _(' '), 
            'modules': ["mysql"],
            'conf': {'class': 'block-2'},
        },        
    ],
}

def get_sections():
    return SECTIONS
    
def get_section(section):
    return SECTIONS_MODULES[section]
    
def get_section_modules(section):
    section = get_section(section)
    modules = []
    for bundle in section:
        for module in bundle['modules']:
            modules.append(module)
    return modules
