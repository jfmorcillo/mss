#!/usr/bin/python 
# -*- coding: UTF-8 -*-

import os
import re
import copy
import imp
import glob
import sys
import logging
import locale
import platform
import xml.etree.ElementTree as ET
from httplib import HTTPSConnection
from unserialize import PHPUnserialize
from sets import Set

from process import ExecManager
from translation import TranslationManager

logging.basicConfig(level=logging.DEBUG)

class ModuleManager:
    """
    Class for managing modules

    """

    def __init__(self, EM, TM):        
        self.modulesDirectory = "modules"
        self.modules = {}
        self.packages = []
        # translation manager
        self.TM = TM
        self.TM.set_catalog('agent')
        global _
        _ = self.TM.translate
        # exec manager
        self.EM = EM
        # logging
        self.logger = logging.getLogger()
        self.load_packages()
        self.load_modules()

    def set_lang(self, lang):
        """ change lang during execution """
        self.TM.set_lang(lang)

    def load_packages(self):
        self.logger.info("Load packages...")
        self.packages = self.EM.load_packages()
        self.logger.info("done.")
        if not self.packages:
            self.logger.info("Error: no packages found")

    def load_modules(self):
        """
        Load all modules at start up
        """
        sys.path.append(self.modulesDirectory)
        modules = self.get_available_modules()
        self.logger.info("Get available mss modules : ")
        for module in modules:
            m = Module(os.path.join(self.modulesDirectory, module), self.TM)
            self.modules[m.id] = m
            self.logger.info(m)

    def get_available_modules(self):
        ret = []
        for item in glob.glob(os.path.join(self.modulesDirectory,
            "*", "__init__.py")):
            ret.append(item.split("/")[1])
        return ret

    def get_modules(self, modules):
        """ return basic info for modules """
        self.logger.info("Get modules info : %s" % str(modules))
        result = {}
        for key, module in self.modules.items():
            if module.id in modules:                  
                # get module packages
                packages = set(module.get_packages())
                # check if packages are installed
                if len(packages) == len(packages.intersection(self.packages)):
                    install = True
                else:
                    install = False
                result[module.id] = {'name': module.name, 'desc': module.desc,
                    'preinst': module.preinst, 'install': install}
        return result

    def preinstall_modules(self, modules):
        """
        get deps for modules to install
        return modules + deps infos
        """
        self.logger.info("Pre-install modules : %s" % str(modules))
        # get deps for modules
        deps = self.check_deps(modules)
        # get modules info
        modules = self.get_modules(modules)
        # get deps info
        deps = self.get_modules(deps)
        return (modules, deps)

    def check_deps(self, modules):
        """ get deps for modules """
        deps = []
        for module in modules:
            if getattr(self.modules[module], 'deps' or None):
                for dep in self.modules[module].deps:
                    self.logger.debug("Add %s module as dep of %s module."
                         % (dep, module))
                    if not dep in modules:
                        try:
                            if self.modules[dep]:
                                deps.append(dep)
                        except KeyError:
                            self.logger.error("Module %s doesn't exists !"
                                % dep)
        return deps

    def get_medias(self, modules):
        """ get medias for modules """
        self.logger.info("Get medias for modules : %s" % str(modules))
        medias_auth_types = Set([])
        medias_auth = []
        medias_done = []
        # get medias for each module
        for module in modules:
            mmedias = self.modules[module].get_medias()
            if len(mmedias) > 0:
                # media need auth
                if mmedias.get("auth"):
                    medias_auth.append(mmedias)
                    medias_auth_types.add(mmedias["auth"])
                # media doesn't need auth, add them
                else:
                    for url in mmedias["urls"]:
                        state, code, output = self.EM.addMedia(mmedias["name"],
                            mmedias["proto"], url)
                        medias_done.append({'name': mmedias["name"],
                            'url': url, 'code': code})

        return (medias_auth, list(medias_auth_types), medias_done)

    def add_media(self, media, login, passwd):
        """ add media with authentication """
        self.logger.info("Add media : %s" % str(media))
        done = []
        fail = []
        old_name = None
        for url in media["urls"]:            
            code, output = self.EM.add_media(media["name"], media["proto"],
                url, login=login, passwd=passwd)
            if code == 0:
                done.append({'type': media["auth"], 'name': media["name"],
                    'url': url, 'code': code})
            # check authentication backend.                    
            else:
                if media["auth"] == "my":
                    self.logger.debug("Check my authentication")
                    code = self.my_auth(login, passwd, media["name"])
                else:
                    code = 3
                # check error code
                if code == 0:
                    err = _("The media seems to be down. Please try later.", "agent")
                elif code == 1:
                    err = _("You don't have access to the media.", "agent")
                elif code == 2:
                    err = _("Bad login/password.", "agent")
                elif code == 3:
                    err = _("Service unavailable. Please try later.", "agent")
                elif code == 4:
                    err = _("Unknow error.", "agent")
                elif code == 5:
                    err = _("Your login does not look like an email address.", "agent")
                self.logger.debug("My authentication returns %s : %s" % (code, err))
                if old_name != media["name"]:
                    fail.append({'type': media["auth"], 'name': media["name"],
                        'url': url, 'code': code, 'err': err})
            old_name = media["name"]
        return (done, fail)

    def my_auth(self, username, password, media):
        # result codes :
        # 0 : product access granted
        # 1 : no product access
        # 2 : bad login
        # 3 : service unavailable
        # 4 : unknow error
        # 5 : login is not an email
    
        # my authentication
        host = "my.mandriva.com"
        url  = "/rest/authenticate.php?username=%s&password=%s&_f=php&return=userData" % (username, re.escape(password))
        # get user data
        conn = HTTPSConnection(host)
        conn.request("GET", url)
        r1 = conn.getresponse()
        # check return code
        if r1.status == 200:
            s_user_data = r1.read()
        else:
            # service unavailable
            return 3
        # unserialize user data
        u = PHPUnserialize()
        user_data = u.unserialize(s_user_data)
        # bad login
        if user_data['code'] == 4 or user_data['code'] == 5:
            return 2
        # login ok
        elif user_data['code'] == 0:
            code = 1
            for key, family in user_data['data']['families'].items():
                if family == "mes5-get-"+media:
                    code = 0
            return code
        elif user_data['code'] == 8:
            return 5

    def install_modules(self, modules):
        """ install modules packages """
        self.logger.info("Install modules : %s" % str(modules))
        packages = []
        for module in modules:
            packages += self.modules[module].get_packages()
        self.logger.debug("Install packages : %s" % str(packages))
        self.EM.install_packages(packages)
        return 0

    def get_config(self, modules):
        """ get modules config """
        self.logger.info("Get config for modules : %s" % str(modules))
        config = {}
        for module in modules:
            config[module] = self.modules[module].get_config()
        print config
        return config

    def valid_config(self, modules, modules_config):
        """ validate user configuration for modules """
        config = {}
        errors = False
        for module in modules:
            module_errors, module_config = self.modules[module].valid_config(modules_config)
            config[module] = module_config
            if module_errors:
                errors = True
        return (errors, config)

    def info_config(self, modules):
        """ check if modules has a config script """
        result = []
        for module in modules:
            path, script, args = self.modules[module].info_config()
            if script:
                result.append(module)
        return result

    def run_config(self, module):
        """ run configuration for module """
        self.logger.debug("Run configuration for %s" % str(module))
        path, script, args = self.modules[module].info_config()
        self.logger.debug("Run script: %s, args: %s" % (str(script), str(args)))
        path = os.path.join(os.getcwd(), path)
        self.EM.run_script(script, args, path)

    def get_state(self):
        """ return execution state """
        return self.EM.get_state()


class Module:
    """
    Base class for all modules instances

    """

    def __init__(self, path, TM):
        self.TM = TM
        self.path = path
        tree = ET.parse(os.path.join(self.path, "desc.xml"))
        self.root = tree.getroot()
        # load module info
        self.load()
        # get module config object
        self.module = None
        # get current module config
        f, p, d = imp.find_module(self.id)
        try:
            # load module
            self.module = imp.load_module(self.id, f, p, d)
        except Exception, err:
            print err

    def load(self):
        """ load module basic infos """
        # get common info
        self.id = self.root.attrib.get("id")
        self.TM.set_catalog(self.id, self.path)
        self._name = self.root.findtext("name")
        self._desc = self.root.findtext("desc")
        # get module deps
        self._deps = [dep.text for dep in self.root.findall("deps/module")]
        # get preinst text
        if self.root.findtext("preinst/text"):
            self._preinst = self.root.findtext("preinst/text")
        else:
            self._preinst = " "

    def get_name(self):
        return _(self._name, self.id)
    name = property(get_name)

    def get_desc(self):
        return _(self._desc, self.id)
    desc = property(get_desc)

    def get_deps(self):
        return self._deps
    deps = property(get_deps)

    def get_preinst(self):
        return _(self._preinst, self.id)
    preinst = property(get_preinst)

    def get_packages(self):
        """ get packages for module """
        if not getattr(self, "packages", None):
            # get packages for current arch
            self.packages = []
            targets = self.root.findall("packages/target")
            for target in targets:
                if target.attrib['name'] == "all" or \
                   target.attrib['name'] == platform.machine():
                    self.packages += [rpm.text for rpm in target.findall("rpm")]
        return self.packages

    def get_medias(self):
        """ get medias for module """
        medias = self.root.find("medias")
        if medias:
            media_auth_backend = medias.attrib.get("auth", None)
            media_proto = medias.attrib.get("proto", "http")
            media_name = medias.attrib.get("name", None)
            urls = medias.findall("url")
            urls = [url.text for url in urls]
            return {'name': media_name, 'auth': media_auth_backend,
                'proto': media_proto, 'urls': urls}
        else:
            return {}

    def get_config(self):
        """ get module current config """
        #if not getattr(self, "config", None):
        self.config = []
        #try:
        current_config = getattr(self.module, 'get_current_config')()
        #except AttributeError:
        #    current_config = {}
        print current_config
        # get XML config
        fields = self.root.findall("config/*")
        for field in fields:
            field_config = field.attrib
            field_help = field.findtext("help")
            field_label = field.findtext("label")
            field_config["help"] = _(field_help, self.id)
            field_config["label"] = _(field_label, self.id)
            field_config["type"] = field.tag
            if field_config["type"] == "options":
                options = field.findall("option")
                field_config["options"] = []
                for option in options:
                    field_config["options"].append(
                        {'name': option.text, 
                         'value': option.attrib.get('value')}
                    )
            # add current value if module is configured
            if current_config.get(field_config['name']):
                field_config['default'] = current_config.get(field_config['name'])
            self.config.append(field_config)
        return self.config

    def valid_config(self, user_config):
        """ valid user configuration for module """
        if not getattr(self, "config", None):
            self.config = self.get_config()

        validated_config = copy.deepcopy(self.config)
        errors = False

        for field in validated_config:

            field_name = field.get("name")
            field_type = field.get("type")

            # set value for networks fields
            if field_type == "network":
                field_value = []
                for user_field, user_value in user_config.items():
                    ip = re.match("^"+self.id+"_"+field_name+"_([0-9]?)_ip$", user_field)
                    if ip:
                        net = ip.group(1)
                        ip = user_config.get(self.id+"_"+field_name+"_"+net+"_ip")
                        mask = user_config.get(self.id+"_"+field_name+"_"+net+"_mask")
                        field_value.append((ip, mask))
                field['default'] = field_value
            elif field_type == "ip":
                field_value = []
                for user_field, user_value in user_config.items():
                    ip = re.match("^"+self.id+"_"+field_name+"_([0-9]?)_ip$", user_field)
                    if ip:
                        net = ip.group(1)
                        ip = user_config.get(self.id+"_"+field_name+"_"+net+"_ip")
                        field_value.append(ip)
                field['default'] = field_value
            # set values for text,password,options fields
            else:
                field_value = user_config.get(self.id+"_"+field_name)
                field["default"] = field_value
        
            if field.get("require"):                         
                if not field_value:
                    errors = True
                    field["error"] = _("This field can't be empty.", "agent")
                elif field_name.endswith("passwd"):
                    field_value2 = user_config.get(self.id+"_"+field_name+"2")
                    if field_value != field_value2:
                        errors = True
                        field["error"] = _("Password mismatch.", "agent")
                else:
                    if field.get("error"):
                        del field["error"]                        

            if field.get("validation"):
                method = getattr(Validation(), field.get("validation"))
                result = method(field_value)
                if result:
                    errors = True
                    field["error"] = _(result, "agent")
                elif field.get("error"):
                    del field["error"]

        # store config if no errors
        if not errors:
            self.config = validated_config

        return (errors, validated_config)

    def info_config(self):
        # get script name and args order
        try:
            script, args = getattr(self.module, 'get_config_info')()
        except AttributeError:
            script, args = (None, [])
        # get args values
        args_values = []
        for arg in args:
            for field in self.config:
                if arg == field['name']:
                    args_values.append(field['default'])
        return (self.path, script, args_values)

    def __str__(self):
        return "%s : %s" % (self.name, self.desc)


class Validation:
    """
    Data validation class

    """

    def fqdn(self, string):
        """ validate hostname """
        if not re.match('^[a-z0-9-\.]+\.[a-z]{2,}$', string):
            return _("Incorrect FQDN.", "agent")
        else:
            return None

if __name__ == '__main__':

    EM = ExecManager()
    TM = TranslationManager()
    MM = ModuleManager(EM, TM)
    #preinst = MM.preInstallModules(["openldap", "dns"])
    #print preinst
#    auths, types, done = MM.get_medias(["openldap"])
#    print auths
    #print types
    #print done
#    for auth in auths:
#        done, fail = MM.add_media(auth, "jpbraun@mandriva.com", "proutt")
#        print done
#        print fail
#    print MM.get_config(['mds-mmc'])
#    MM.info_config(['openldap', 'dns'])
#    MM.run_config('openldap')
#    MM.install_modules(['openldap'])
#    print _("The media seems to be down. Please try later.", "agent")
#    MM.set_lang('')
#    print _("The media seems to be down. Please try later.", "agent")
#    MM.set_lang('fr_FR')
#    print _("The media seems to be down. Please try later.", "agent")    
#    print MM.get_modules(['openldap'])
