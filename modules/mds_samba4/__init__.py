import re
from mss.agent.managers.translation import TranslationManager
from mss.agent.lib.utils import get_domain
import netifaces
from IPy import IP

_ = TranslationManager().translate


def get_config_info():
    return ("setup-samba4.sh", ["smb_mode", "smb_domain", 'admin', "smb_passwd", "net", 'dns_ip'])


def valid_domain(string):
    """Validate domain input"""
    from socket import gethostname
    hostname = gethostname()

    if not re.match("^[A-Z0-9-]+(\\.[A-Z0-9-]+)*(\\.[A-Z]{2,})$", string, re.IGNORECASE):
        return _("Incorrect SAMBA domain name, use only alphanumeric characters and dots.", "mds_samba4")
    elif string.split('.')[0] == hostname:
        return _("Incorrect SAMBA domain name, Must NOT start with short host name.", "mds_samba4")
    else:
        return None


def valid_mode(mode):
    if mode == '':
        return _('Please select a mode', 'mds_samba4')
    else:
        return None


def valid_password(passwd):
    if len(passwd) < 8:
        return _("Password must be at least 8 characters long", "mds_samba4")
    if not re.search("[0-9]", passwd):
        return _("Password must have at least one number", "mds_samba4")
    if not re.search("[A-Z]", passwd):
        return _("Password must have at least one capital letter", "mds_samba4")
    if not re.search("[a-z]", passwd):
        return _("Password must have at least one lowercase letter", "mds_samba4")
    return None


def get_custom_config(config):

    config.append({'slug': 'mds_samba4',
                   "type": "options",
                   "name": "smb_mode",
                   "require": "yes",
                   "label": "Mode",
                   'validation': 'valid_mode',
                   "help": "Which type of provisioning of SAMBA 4",
                   "options": [
                       {'name': '',
                        'value': ''},
                       {"name": "Create a new Active Directory domain",
                        "value": "dc"},
                       {"name": "Join an existing Active Directory domain",
                        "value": "bdc",
                        'toggle': ['dns_ip', 'admin']}]})

    from mmc.plugins.shorewall import get_zones, get_zones_interfaces
    zones = get_zones('lan')
    interfaces = get_zones_interfaces(zones)
    options = []
    for interface in interfaces:
        if_detail = netifaces.ifaddresses(interface[1])
        # check interface is configured
        if netifaces.AF_INET in if_detail:
            addr = if_detail[netifaces.AF_INET][0]['addr']
            netmask = if_detail[netifaces.AF_INET][0]['netmask']
            network = str(IP(addr).make_net(netmask).net())
            options.append({'name': interface[0] + '(' + network + ')',
                            'value': interface[1]})

    config.append({'slug': 'mds_samba4',
                   'name': 'net',
                   'require': 'yes',
                   'label': _('Network', 'mds_samba4'),
                   'help': _('Choose the network for the DNS zone and DHCP.', 'mds_samba4'),
                   'type': 'options',
                   'options': options})
    domain = get_domain()
    config.append({'slug': 'mds_samba4',
                   'type': 'text',
                   'name': 'smb_domain',
                   'require': 'yes',
                   'default': domain,
                   'validation': 'valid_domain',
                   'label': _('SAMBA domain name', 'mds_samba4'),
                   'help': _('The name of your Microsoft domain. Use only alphanumeric characters '
                             'and dots like: mandriva.int. It Must NOT start with short host name.',
                             'mds_samba4')
                   })
    config.append({'slug': 'mds_samba4',
                   'type': 'text',
                   'name': 'dns_ip',
                   'require': 'yes',
                   'default': '',
                   'validation': 'ip',
                   'label': _('DNS server IP', 'mds_samba4'),
                   'help': _('The IP address of the DNS server', 'mds_samba4')
                   })
    config.append({'slug': 'mds_samba4',
                   "type": "text",
                   "name": "admin",
                   "require": "yes",
                   'default': '',
                   "label": "Administrator account",
                   "help": "Account name of the Administrator."
                   })
    config.append({'slug': 'mds_samba4',
                   "type": "password",
                   "name": "smb_passwd",
                   "require": "yes",
                   "validation": "valid_password",
                   "label": "Administrator password",
                   "help": "Password for the Microsoft domain Administrator account. Password must be composed, at least, of 8 characters with one number, one capital letter and one lowercase letter."
                   })

    return config
