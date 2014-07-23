#!/usr/bin/env python
import sys
import fileinput
import os
import shutil
import socket
import subprocess
from time import sleep
from mmc.plugins.samba4.smb_conf import SambaConf


SLEEP_TIME = 1  # Sleep time between each check
DESCRIPTION = "Mandriva Directory Server - SAMBA %v"


def fail_provisioning_samba4(msg=None):
    if msg:
        print "ERROR:\n\t%s" % msg
    print "SAMBA 4 provisioning has failed"
    sys.exit(1)


def shlaunch(cmd, ignore=False):
    if not ignore:
        print "$ %s" % cmd
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    exit_code = p.wait()
    stdout = "".join(p.stdout.readlines())
    if exit_code != 0:
        print "ERROR executing `%s`:\n%s" % (cmd, stdout)
        fail_provisioning_samba4()
    if not ignore:
        print stdout
    return stdout


def provision_samba4(mode, realm, admin_password):
    if mode != 'dc':
        fail_provisioning_samba4("We can only provision samba4 as Domain Controller")

    samba = SambaConf()
    params = {'realm': realm, 'prefix': samba.prefix,
              'role': mode, 'adminpass': admin_password,
              'workgroup': samba.workgroupFromRealm(realm)}

    def provision_domain():
        print "Provisioning domain"
        cmd = ("%(prefix)s/bin/samba-tool domain provision"
               " --adminpass='%(adminpass)s'"
               " --domain='%(workgroup)s'"
               " --workgroup='%(workgroup)s'"
               " --realm='%(realm)s'"
               " --use-xattr=yes"
               " --use-rfc2307"
               " --server-role='%(role)s'" % params)
        shlaunch(cmd)

    def write_config_files():
        print "provision: domain_provision_cb"
        netbios_domain_name = shlaunch("hostname", ignore=True).strip()
        samba.writeSambaConfig(mode, netbios_domain_name, realm, DESCRIPTION)
        samba.writeKrb5Config(realm)

    def disable_password_complexity():
        print "provision: disable_password_complexity"
        cmd = ("%s/bin/samba-tool domain passwordsettings set"
               " --complexity=off"
               " --min-pwd-length=0"
               " --min-pwd-age=0"
               " --max-pwd-age=999" % samba.prefix)
        shlaunch(cmd)

    def check_ldap_is_running():
        # Number of times we will check whether ldap is running on 389 port
        max_checkings_ldap_running = 10
        tries = 1
        while tries < max_checkings_ldap_running:
            print "Checking ldap is running"
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', 389))
            if result == 0:
                return True
            sleep(SLEEP_TIME)
            tries += 1
        fail_provisioning_samba4("Ldap is not running after waiting long time")

    def openldap_smb5pwd_config():
        f = open('/etc/openldap/slapd.conf', 'r')
        for line in f:
            if line.lstrip().startswith('moduleload') and 'smbk5pwd' in line:
                return
        f.close()
        state = 0
        for line in fileinput.input('/etc/openldap/slapd.conf', inplace=1):
            print line,
            if state == 0:
                if line.lstrip().startswith('moduleload'):
                    print 'moduleload smbk5pwd.so'
                    state = 1
            elif state == 1:
                if line.lstrip().startswith('database'):
                    print 'overlay smbk5pwd'
                    state = 2
        shlaunch("chown root:ldap /etc/openldap/slapd.conf")

    def reconfig_ldap_service():
        print "Reconfiguring ldap service"
        openldap_smb5pwd_config()
        should_reconfing = True
        f = None
        try:
            f = open('/etc/sysconfig/ldap', 'r')
            for line in f:
                if line.lstrip().startswith('SLAPDURLLIST='):
                    should_reconfing = False
            if should_reconfing:
                f.close()
                f = open('/etc/sysconfig/ldap', 'a')
                f.write(os.linesep)
                f.write('SLAPDURLLIST="ldap://127.0.0.1"')
                f.write(os.linesep)
                f.close()
            shlaunch("service ldap restart")
        except Exception as e:
            fail_provisioning_samba4(e.message)
        sleep(SLEEP_TIME)
        check_ldap_is_running()

    def stop_iptables_services():
        print "Stopping iptables service"
        shlaunch("service iptables stop")

    def start_samba4_service():
        print "Starting samba4 service"
        shlaunch("service samba4 start")
        sleep(SLEEP_TIME)

    def start_s4sync_service():
        print "Starting s4sync daemon"
        shlaunch("service s4sync start")

    # Clean up previous provisions
    if os.path.exists(os.path.join(samba.prefix, 'etc/smb.conf')):
        os.unlink(os.path.join(samba.prefix, 'etc/smb.conf'))
    if os.path.exists(os.path.join(samba.prefix, 'private/sam.ldb')):
        for root, dirs, files in os.walk(os.path.join(samba.prefix, 'private/')):
            for f in files:
    	        os.unlink(os.path.join(root, f))
            for d in dirs:
    	        shutil.rmtree(os.path.join(root, d))

    provision_domain()
    disable_password_complexity()
    write_config_files()

    reconfig_ldap_service()
    stop_iptables_services()

    start_samba4_service()
    start_s4sync_service()

provision_samba4(*sys.argv[1:])
