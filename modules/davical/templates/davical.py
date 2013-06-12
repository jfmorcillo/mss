"""
Davical MMC hooks
"""

import os
import pwd
import subprocess
import socket


USER = "apache"

def demote(user_uid, user_gid):
    def result():
        os.setgid(user_gid)
        os.setuid(user_uid)
    return result

def sync_davical_users():
    pw_record = pwd.getpwnam(USER)
    user_name = pw_record.pw_name
    user_home_dir = pw_record.pw_dir
    user_uid = pw_record.pw_uid
    user_gid = pw_record.pw_gid
    env = os.environ.copy()
    env['HOME']  = user_home_dir
    env['LOGNAME']  = user_name
    env['USER']  = user_name
    fqdn = socket.getfqdn()
    process = subprocess.Popen(["/usr/bin/php",
                                "/usr/share/davical/scripts/cron-sync-ldap.php", fqdn],
                               preexec_fn=demote(user_uid, user_gid), env=env)
    process.wait()

# MMC hook
def base_adduser(entry):
    sync_davical_users()

# MMC hook
def base_deluser(entry):
    sync_davical_users()


if __name__ == "__main__":
    sync_davical_users()
