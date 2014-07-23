import re
from mss.agent.managers.translation import TranslationManager

_ = TranslationManager().translate


def get_config_info():
    return ("setup-samba4.sh", ["smb_mode", "smb_domain", "smb_passwd"])

def valid_domain(string):
    """Validate domain input"""
    if not re.match("^[A-Z0-9-]+(\\.[A-Z0-9-]+)*(\\.[A-Z]{2,})$", string, re.IGNORECASE):
        return _("Incorrect SAMBA domain name.", "mds_samba4")
    else:
        return None
