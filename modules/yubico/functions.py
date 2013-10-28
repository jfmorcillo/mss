import socket
import os
import re
import time
import shutil
import tempfile
#from mmc.plugins.services.manager import ServiceManager
import systemd_dbus.manager
import logging

logger = logging.getLogger()
logging.getLogger('').addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

class MSSConfig:
    def __init__(self):
        #check root
        if os.geteuid() != 0:
            error("Error, must be root user")
            exit (1)
        self.server = '127.0.0.1'
        self.host = socket.gethostname()
        self.fqdn = socket.getfqdn()
        self.domain = self.fqdn.split('.', 1)[1]
        
        #check mmc configured
        mds_base_ini = "/etc/mmc/plugins/base.ini"
        if not os.path.exists(mds_base_ini):
            error("MC interface is not installed.")
            error("an't continue.")
            exit (1)
        else:
            self.mdsserver = '127.0.0.1'
            mds_conf = open(mds_base_ini, "r")
            for line in mds_conf:
                #MDSSUFFIX=`grep '^baseDN' $MDS_BASE_INI | sed 's/^.*[[:space:]]\+=[[:space:]]\+//'`
                if re.search('^baseDN', line):
                    self.mdssuffix = re.sub('^.*[[:space:]]\+=[[:space:]]\+','',line)
                    
                #MDSPASS=`grep '^password ' $MDS_BASE_INI | sed 's/^.*[[:space:]]\+=[[:space:]]\+//'`
                if re.search('^password ', line):
                    self.pasword = re.sub('^.*[[:space:]]\+=[[:space:]]\+','',line)
                    
# mdspass_e = escape_sed mdspass

class ConfigFile:
    def __init__(self, src):
        self.src = src

    def copy(self, dst):
        d = os.path.dirname(dst)
        if not os.path.exists(d):
            os.makedirs(d)
        shutil.copy2(self.src, dst)


class LDAPSchema():
    def __init__(self, src):
        self.src = src

    def add_schema(self):
        logger.debug('add_schema')
        schema = os.path.basename(self.src)
        notmatched = True
        with open('/etc/openldap/schema/local.schema') as inputfile:
            for line in inputfile:
                if schema in line:
                    logging.getLogger().debug('schema matched')
                    print(line)
                    notmatched = False
                    break
        dst = '/etc/openldap/schema/' + schema
        if notmatched:
            with open('/etc/openldap/schema/local.schema', 'a') as myfile:
                
                myfile.write('include ' + dst + '\n')
        shutil.copy(self.src, dst)
        os.chmod(dst, 0644)
        print('Schema %s added to OpenLDAP' %schema)
        restart_service('ldap.service')


# $1: *file* to be backed up
def backup(filename):
    now = time.time()
    if not os.path.exists(filename):
        print('No file to backup (%s)', filename)

    newname = filename + now
    if os.path.isdir(filename):
        shutil.copytree(filename, newname, True)
    else:
        shutil.copy2 (filename, newname)
    print newname

#some kind of sed -i implementation
def sed(pattern, repl, filename):
    with tempfile.NamedTemporaryFile() as tmpFile:
        with open(filename) as inputFile:
            for line in inputFile:
                tmpFile.write(re.sub(pattern, repl, line))
        shutil.move(tmpFile.name, inputFile.name)

def restart_service(serviceName):
    systemd_dbus.manager.Manager().restart_unit(serviceName, 'replace')

def info_b(msg):
    print('8%s', msg)

def info(msg):
    print('7%s', msg)

def error(msg):
    print('2%s', msg)

def warning(msg):
    print('1%s', msg)
