from mss.agent.lib.utils import grep

def check_configured():
    return grep('mirror.mandriva.com/mbs1_updates/x86_64', '/etc/urpmi/urpmi.cfg')

