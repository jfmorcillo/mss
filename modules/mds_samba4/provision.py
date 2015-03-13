#!/usr/bin/env python
# coding=utf-8
import sys
import fileinput
import os
import shutil
import socket
from socket import gethostname
import subprocess
from time import sleep, time
import netifaces
from IPy import IP
import ldap
from threading import Thread, Event

from mmc.plugins.samba4.smb_conf import SambaConf
from mmc.plugins.network import zoneExists, getSubnet, addSubnet, addZone, addRecord, setSubnetAuthoritative, setSubnetOption, addPool, setSubnetDescription
from mmc.plugins.network import addRecordA, setHostAliases
from mmc.plugins.shorewall import get_zones, add_rule


SLEEP_TIME = 1  # Sleep time between each check
DESCRIPTION = "Mandriva Directory Server - SAMBA %v"


class ReadFlux(Thread):

    """Reads Popen stdout and stderr
    """

    def __init__(self, pipe):
        Thread.__init__(self)
        self.pipe = pipe
        self._stop = Event()

    def record_line(self, line):
        if line:
            print(line.strip())

    def run(self):
        while not self._stop.is_set():
            line = self.pipe.readline()
            self.record_line(line)

    def stop(self):
        self._stop.set()
        # get last lines
        for line in self.pipe.readlines():
            self.record_line(line)


def run_async(cmd, **kwargs):
    os.environ['LC_ALL'] = 'C'
    print("Running command '%s'" % cmd)
    print('kwargs: %s' % kwargs)
    process = subprocess.Popen(cmd, **kwargs)
    return process


def run(cmd, **kwargs):
    """Launch a cmd synchronously.
    """
    if 'stdout' in kwargs:
        kwargs.pop('stdout')
    if 'stderr' in kwargs:
        kwargs.pop('stderr')

    process = run_async(cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        **kwargs)

    err_reader = ReadFlux(process.stderr)
    err_reader.start()
    std_reader = ReadFlux(process.stdout,)
    std_reader.start()

    exit_code = process.wait()

    err_reader.stop()
    std_reader.stop()

    if exit_code != 0:
        print("ERROR executing `%s`" % cmd)
        fail_provisioning_samba4()


def backup(filename):
    backuped = filename + '.' + str(time())
    shutil.copyfile(filename, backuped)
    return backuped


def fail_provisioning_samba4(msg=None):
    if msg:
        print("ERROR:\n\t%s" % msg)
    print("SAMBA 4 provisioning has failed")
    sys.exit(1)


def shlaunch(cmd, ignore=False, stderr=subprocess.STDOUT):
    if not ignore:
        print("$ %s" % cmd)
    p = subprocess.Popen(cmd, shell=True,
                         stdout=subprocess.PIPE,
                         stderr=stderr)
#     exit_code = p.wait()
    (stdout, _) = p.communicate()
    exit_code = p.returncode
#    stdout = "".join(p.stdout.readlines())
    if exit_code != 0:
        print("ERROR executing `%s`:\n%s" % (cmd, stdout))
        fail_provisioning_samba4()
    if not ignore:
        print(stdout)
    return stdout


def provision_samba4(mode, realm, admin, admin_password, iface, dns_ip):
    if mode not in ['dc', 'bdc', 'robdc']:
        fail_provisioning_samba4(
            "We can only provision samba4 as Domain Controller")

    print('Provisionning samba mode: %s, realm: %s, admin_password:%s' %
          (mode, realm, admin_password))

    bdc = False
    rodc = False
    if mode == 'bdc':
        mode = 'dc'
        bdc = True
    elif mode == 'robdc':
        mode = 'dc'
        bdc = True
        rodc = True

    samba = SambaConf()
    params = {'realm': realm, 'prefix': samba.prefix,
              'role': mode, 'adminpass': admin_password,
              'workgroup': samba.workgroupFromRealm(realm)}

    def provision_domain():
        print("Provisioning domain")
        cmd = ("%(prefix)s/bin/samba-tool domain provision"
               " --dns-backend='BIND9_FLATFILE'"
               " --adminpass='%(adminpass)s'"
               " --domain='%(workgroup)s'"
               " --workgroup='%(workgroup)s'"
               " --realm='%(realm)s'"
               " --use-xattr=yes"
               " --use-rfc2307"
               " --server-role='%(role)s'" % params)
        shlaunch(cmd)

    def join_domain():
        print('Joining domain')
        if bdc is True:
            if rodc is True:
                mode_bdc = 'RODC'
            else:
                mode_bdc = 'DC'
        else:
            fail_provisioning_samba4('Unsupported DC mode.')

        par = {'realm': realm,
               'mode_bdc': mode_bdc,
               'prefix': samba.prefix,
               'username': admin,
               'adminpass': admin_password}
        cmd = ("%(prefix)s/bin/samba-tool domain join %(realm)s %(mode_bdc)s"
               " --username='%(username)s'"
               " --realm='%(realm)s'"
               " --password='%(adminpass)s'" % par)
        # shlaunch(cmd)
        run(cmd, shell=True)

    def write_config_files():
        print("provision: domain_provision_cb")
        netbios_domain_name = gethostname()

        samba.writeSambaConfig(mode, netbios_domain_name, realm, DESCRIPTION)
        samba.writeKrb5Config(realm)

    def disable_password_complexity():
        print("provision: disable_password_complexity")
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
            print("Checking ldap is running")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', 389))
            if result == 0:
                return True
            sleep(SLEEP_TIME)
            tries += 1
        fail_provisioning_samba4("Ldap is not running after waiting long time")

    def openldap_smb5pwd_config():
        with open('/etc/openldap/slapd.conf', 'r') as h:
            for line in h:
                if line.lstrip().startswith('moduleload') and 'smbk5pwd' in line:
                    return
        state = 0
        conf_file = '/etc/openldap/slapd.conf'
        backup_file = backup(conf_file)
        with open(conf_file, 'w') as file_out, open(backup_file, 'r') as file_in:
            for line in file_in:
                file_out.write(line)
                if state == 0:
                    if line.lstrip().startswith('moduleload'):
                        file_out.write('moduleload smbk5pwd.so\n')
                        state = 1
                elif state == 1:
                    if line.lstrip().startswith('database'):
                        file_out.write('overlay smbk5pwd\n')
                        state = 2
        # TODO: fix this strange chmodS
        shlaunch("chown root:ldap /etc/openldap/slapd.conf")

    def reconfig_ldap_service():
        print("Reconfiguring ldap service")
        openldap_smb5pwd_config()
        should_reconfing = True
        f = None
        try:
            f = open('/etc/sysconfig/slapd', 'r')
            for line in f:
                if line.lstrip().startswith('SLAPDURLLIST='):
                    should_reconfing = False
            if should_reconfing:
                f.close()
                f = open('/etc/sysconfig/slapd', 'a')
                f.write(os.linesep)
                f.write('SLAPDURLLIST="ldap://127.0.0.1"')
                f.write(os.linesep)
                f.close()
            shlaunch("systemctl restart slapd")
        except Exception as e:
            print(">>>> %s" % e)
            fail_provisioning_samba4(e.message)
        sleep(SLEEP_TIME)
        check_ldap_is_running()

    def clean_etc_host():
        cmd = "sed -i -e 's/.*%s.*//' /etc/hosts" % gethostname()
        shlaunch(cmd)

    def configure_network():

        def configure_ntpd():
            shlaunch("systemctl stop ntpd")
            state = 0
            for line in fileinput.input('/etc/ntp.conf', inplace=1):
                # replace first server
                if line.startswith('fudge'):
                    print(line,)
                    state = 1
                if line.startswith('server') and state == 1:
                    print('server %s' % dns_ip)
                    state = 2
                else:
                    print(line,)
            shlaunch("ntpdate %s" % dns_ip)
            shlaunch("systemctl start ntpd")

        def update_resolvconf():
            with open('/etc/dhclient-enter-hooks', 'w') as f:
                fic = """make_resolv_conf() {
    echo "nameserver %s" > /etc/resolv.conf
    echo "nameserver 127.0.0.1" >> /etc/resolv.conf
    echo "search %s" >> /etc/resolv.conf
}""" % (dns_ip, realm)
                f.write(fic)

        def add_dns():
            base_dn = ",".join(map(lambda p: "DC=%s" % p, realm.split('.')))
            bind_dn = 'CN=%s,CN=Users,%s' % (admin, base_dn)
            dns_dn = 'OU=Domain Controllers,%s' % base_dn
            l = ldap.initialize('ldap://%s:389' % dns_ip)
            l.bind_s(bind_dn, admin_password)
            entries = l.search_s(dns_dn,
                                 ldap.SCOPE_ONELEVEL,
                                 filterstr='(&(samAccountType=805306369)(primaryGroupID=516)(objectCategory=computer))',
                                 attrlist=['dn',
                                           'dNSHostName',
                                           'distinguishedName',
                                           'servicePrincipalName'])
            for e in entries:
                rec = {'cname': None}
                if e[0] is None:
                    continue

                for key in e[1].keys():
                    #             print(e[1][key])
                    if key == 'servicePrincipalName':
                        for name in e[1][key]:
                            if name.startswith('ldap/') and name.endswith('_msdcs.%s' % realm):
                                rec['cname'] = ('.').join(
                                    name.split('.')[0:2])[5:]
                    if key == 'dNSHostName':
                        rec['dNSHostName'] = e[1][key][0]
                print(rec)

                fqdn = rec['dNSHostName'].split('.')
                hostname = fqdn[0]
                zone = '.'.join(fqdn[1:])
                alias = rec['cname']
                if zone and hostname and alias:
                    try:
                        print(
                            'addRecordA(%s,%s,%s)' % (zone, hostname, dns_ip))
                        addRecordA(zone, hostname, dns_ip)
                    except ldap.ALREADY_EXISTS as ex:
                        print(ex)

                    print(
                        'setHostAliases(%s,%s,%s)' % (zone, hostname, [alias]))
                    setHostAliases(zone, hostname, [alias])

        def configure_shorewall():
            print("Configure shorewall")
            src = os.path.join(os.getcwd(), 'templates',
                               'shorewall_macro.Samba4AD')
            dst = os.path.join('/etc/shorewall/', 'macro.Samba4AD')
            shutil.copy(src, dst)
            os.chmod(dst, 0o600)

            zones = get_zones('lan')
            for zone in zones:
                add_rule('Samba4AD/ACCEPT', zone, "fw")

            shlaunch("systemctl restart shorewall")

        def configure_dns():
            print("Configure dns for zone %s" % realm)
            if not zoneExists(realm):
                addZone(realm,
                        network,
                        netmask,
                        reverse=True,
                        description='AD network',
                        nameserver=nameserver,
                        nameserverip=addr)

            rec = {'_ldap._tcp': '0 0 389',
                   '_kerberos._tcp': '0 0 88',
                   '_ldap._tcp.dc._msdcs': '0 0 389',
                   '_kerberos._tcp.dc._msdcs': '0 0 88'}
            for key, val in rec.items():
                try:
                    if addRecord(zone=realm,
                                 type='SRV',
                                 hostname=key,
                                 value=val + ' ' + nameserver):
                        print('Created SRV record \'%s %s\'' %
                              (key, val + ' ' + nameserver))
                except:
                    print('Check that SRV record \'%s %s\' exists in your DNS' %
                          (key, val + ' ' + nameserver))
            if bdc:
                add_dns()
                update_resolvconf()

            shlaunch("systemctl restart named-sdb")
            print("### Done configure_dns")

        def configure_dhcp():
            subnet = getSubnet(network)
            if not subnet:
                addSubnet(network, netmask, realm)
                setSubnetDescription(network, 'AD network')
                setSubnetAuthoritative(network)
                setSubnetOption(network, 'domain-name', '\"' + realm + '\"')
                setSubnetOption(network, 'domain-name-servers', addr)
                start = IP(ip.net().int() + 100)
                end = IP(start.int() + 99)
                addPool(network, 'ADpool', str(start), str(end))
                shlaunch("systemctl restart dhcpd")
            print("### Done configure_dhcp")

        if_detail = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]
        addr = if_detail['addr']
        netmask = if_detail['netmask']
        ip = IP(addr).make_net(netmask)
        network = str(ip.net())
        netmask = ip.prefixlen()
        nameserver = gethostname()

        configure_dns()
        if not bdc:
            configure_dhcp()
        else:
            configure_ntpd()

        configure_shorewall()
        print("### Done configure_shorewall")

    def start_samba4_service():
        print("Starting samba service")
        shlaunch("systemctl restart samba")
        sleep(SLEEP_TIME)

    def start_s4sync_service():
        print("Starting s4sync daemon")
        shlaunch("systemctl start s4sync")

    # Clean up previous provisions
    if os.path.exists(samba.smb_conf_path):
        os.unlink(samba.smb_conf_path)
    if os.path.exists(os.path.join(samba.db_dir, 'private/sam.ldb')):
        for root, dirs, files in os.walk(os.path.join(samba.db_dir, 'private/')):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

    write_config_files()
    print("### Done write_config_files")

    if not bdc:
        provision_domain()
        print("### Done provision_domain")
        disable_password_complexity()
        print("### Done disable_password_complexity")
    else:
        clean_etc_host()
        join_domain()

    reconfig_ldap_service()
    print("### Done reconfig_ldap_service")

    configure_network()

    start_samba4_service()
    print("### Done start_samba4_service")
    start_s4sync_service()
    print("### Done start_s4sync_service")


provision_samba4(*sys.argv[1:])
