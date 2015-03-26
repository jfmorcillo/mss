import re
from mss.agent.managers.translation import TranslationManager
from mss.agent.lib.utils import get_domain
import netifaces
from IPy import IP

_ = TranslationManager().translate


def get_config_info():
    return ("setup-samba4.sh", ["smb_mode", "smb_domain", 'admin',
                                "smb_passwd", "net", "dns_ip", "smb_forwarder"])


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
    errors = []
    if len(passwd) < 8:
        errors.append(_("Password must be at least 8 characters long", "mds_samba4"))
    if not re.search("[0-9]", passwd):
        errors.append(_("Password must have at least one number", "mds_samba4"))
    if not re.search("[A-Z]", passwd):
        errors.append(_("Password must have at least one capital letter", "mds_samba4"))
    if not re.search("[a-z]", passwd):
        errors.append(_("Password must have at least one lowercase letter", "mds_samba4"))
    if errors:
        return "\n".join(errors)
    return None


def get_custom_config(config):
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

    return config
