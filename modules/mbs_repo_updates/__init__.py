from mss.agent.lib.utils import grep

def check_configured():
    return grep('mirror.mandriva.com/factory/x86_64', '/etc/urpmi/urpmi.cfg')
