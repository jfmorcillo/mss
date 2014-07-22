from mss.agent.lib.utils import grep

def get_config_info():
    return ('setup-repo.sh', [])

def check_configured():
    return grep('zentyal_jgarcia', '/etc/urpmi/urpmi.cfg')
