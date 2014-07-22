import os

def get_config_info():
    return ('setup-repo.sh', [])

def check_configured():
    repo_added = os.system("grep \"^Core\\\\\\ Updates\\\\\\ Testing http\" /etc/urpmi/urpmi.cfg") == 0
    if not repo_added:
        return False
    repo_ignored = os.system("grep -A1 \"^Core\\\\\\ Updates\\\\\\ Testing http\" /etc/urpmi/urpmi.cfg | grep ignore") == 0
    return not repo_ignored
