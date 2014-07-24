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
