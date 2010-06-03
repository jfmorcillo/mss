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
import xmlrpclib
import sqlite3
from datetime import datetime
import xml.etree.ElementTree as ET
from IPy import IP
from httplib import HTTPSConnection
from unserialize import PHPUnserialize
from sets import Set

from process import ExecManager
from translation import TranslationManager
    
logging.basicConfig(level=logging.DEBUG)

def expose(f):
    "Decorator to set exposed flag on a function."
    f.exposed = True
    return f

def is_exposed(f):
    "Test whether another function should be publicly exposed."
    return getattr(f, 'exposed', False)


class ModuleManager:
    """
    Class for managing modules

    """

    def _dispatch(self, method, params):
        func = getattr(self, method)            
        if not is_exposed(func):
            raise Exception('Method "%s" is not supported' % method)
        
        return func(*params)

    def __init__(self, EM, TM):        
        self.modulesDirectory = os.path.join(os.path.dirname(__file__), "modules")
        self.modules = {}
        self.packages = []
        # BDD access
        self.conn = sqlite3.connect('/var/lib/mss/mss-agent.db')
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
        self.update_medias()
        self.load_modules()

    @expose
    def set_lang(self, lang):
        """ change lang during execution """
        self.logger.info("Lang changed to %s" % lang)
        self.TM.set_lang(lang)

    @expose
    def load_packages(self):
        self.logger.info("Load packages...")
        self.EM.load_packages(self.set_packages)

    def set_packages(self, code, output):
        if code == 0:
            packages = output.split('#')
            if not packages:
                self.logger.error("No packages found.")
            else:
                self.packages = packages
                self.logger.info("Loading packages done.")
        else:
            self.logger.error("Can't load packages.")

    @expose
    def update_medias(self):
        self.EM.update_medias()

    def load_modules(self):
        """
        Load all modules at start up
        """
        sys.path.append(self.modulesDirectory)
        modules = self.get_available_modules()
        self.logger.info("Get available mss modules : ")
        for module in modules:
            self.logger.debug("Loading %s" % module)
            m = Module(os.path.join(self.modulesDirectory, module), self.TM)
            self.modules[m.id] = m
            self.logger.info(m)

    def get_available_modules(self):
        ret = []
        for item in glob.glob(os.path.join(self.modulesDirectory,
            "*", "__init__.py")):
            ret.append(item.split("/")[-2])
        return ret

    @expose
    def get_modules(self, modules):
        """ return basic info for modules """
        self.logger.info("Get modules info : %s" % str(modules))
        result = []
        for m in modules:
            if m in self.modules:
                module = self.modules[m]
                # get module packages
                packages = set(module.get_packages())                
                # check if packages are installed
                if len(packages) == len(packages.intersection(self.packages)):
                    installed = True
                else:
                    installed = False
                # check if module is configured
                c = self.conn.cursor()
                c.execute('select * from module where name=?', (m,))
                if c.fetchone():
                    configured = True 
                else:
                    configured = False
                c.close()
                # return result
                result.append({ 'id': module.id, 'name': module.name, 
                    'desc': module.desc, 'url': module.url, 'buy': module.buy,
                    'preinst': module.preinst, 'installed': installed, 
                    'configured': configured, 'conflict': [], 
                    'conflicts': module.conflicts })
        # check conflicts between modules
        for m in result:
            if m['conflicts']:
                for m1 in m['conflicts']:
                    for m2 in result:
                        if m1 == m2['id'] and m2['installed']:
                            m['conflict'].append(m2['id'])
        return result

    @expose
    def preinstall_modules(self, modules):
        """
        get deps for modules to install
        return modules infos
        """
        # force module re-installation
        force_modules = []
        for m in modules:
            if m.startswith("force-"):
                force_modules.append(m.replace("force-", ""))
        modules = [ m.replace("force-","") for m in modules ]
        # store old modules list
        old = modules
        # get deps for modules
        modules = self.check_deps(modules, [])
        modules = self.order_deps(modules)
        # get difference for dep list
        deps = list(set(modules).difference(old))
        # get modules info (modules + deps)
        modules = self.get_modules(modules)
        # remove already configured modules unless force
        modules = [ m for m in modules if not m['configured'] or m['id'] in force_modules ]
        # tell if the module is an dependency of selected modules
        # or if we reinstall it
        for m in modules:
            if m['id'] in deps:
                m['dep'] = True
            else:
                m['dep'] = False
            if m['id'] in force_modules:
                m['force'] = True
            else:
                m['force'] = False
        self.logger.info("Pre-install modules : %s" % str(modules))
        return modules

    def order_deps(self, modules, cnt=1):
        for module in modules:
            # if the module has deps and is not indexed
            if module[1] and module[2] == -1:
                # for each dep of current module
                set_index = True
                for m1 in module[1]:
                    # for each module
                    for m2 in modules:
                        # if the dep is not indexed (not >=0)
                        if m1 == m2[0] and not m2[2] >= 0:
                            set_index = False
                # set the current module index to cnt
                # if all deps are indexed
                if set_index:
                    module[2] = cnt

        # make 3 pass to determine indexes
        if(cnt < 4):
            cnt += 1
            modules = self.order_deps(modules, cnt)
        # calcule module list from indexes
        else:
            result = []
            for i in range(cnt):
                for module in modules:
                    if module[2] == i:
                        if not module[0] in result:
                            result.append(module[0])
            modules = result
        return modules

    def check_deps(self, modules, dependencies):
        """ get deps for modules
            create a list with the form : [ [ module, [deps], index ],... ]
        """
        for module in modules:
            deps = self.get_deps(module)
            if deps:
                # set the index a -1 to calculate index
                dependencies.append([module, deps, -1])
                dependencies = self.check_deps(deps, dependencies)
            else:
                # set the index at 0 as the module has no deps
                dependencies.append([module, None, 0])
        return dependencies

    def get_deps(self, module):
        """ get deps for module """
        if getattr(self.modules[module], 'deps' or None):
            deps = []
            for dep in self.modules[module].deps:
                try:
                    if self.modules[dep]:
                        deps.append(dep)
                except KeyError:
                    self.logger.error("Module %s doesn't exists !"
                        % dep)
            return deps
        return None

    @expose
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

    @expose
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
                if not login or not passwd:
                    code = 2
                elif media["auth"] == "my":
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

    @expose
    def install_modules(self, modules):
        """ install modules packages """
        self.logger.info("Install modules : %s" % str(modules))
        packages = []
        for module in modules:
            packages += self.modules[module].get_packages()
        if packages:
            self.logger.debug("Install packages : %s" % str(packages))
            self.EM.install_packages(packages)
            return True
        else:
            self.logger.info("No packages to install")
            return False

    @expose
    def get_config(self, modules):
        """ get modules config """
        self.logger.info("Get config for modules : %s" % str(modules))
        config = []
        for module in modules:
            config.append(self.modules[module].get_config())
        return config

    @expose
    def valid_config(self, modules, modules_config):
        """ validate user configuration for modules """
        config = []
        errors = False
        for module in modules:
            module_errors, module_config = self.modules[module].valid_config(modules_config)
            config.append(module_config)
            if module_errors:
                errors = True
        return (errors, config)

    @expose
    def run_config(self, module):
        """ run configuration for module """
        self.logger.debug("Run configuration for %s" % str(module))
        path, script, args = self.modules[module].info_config()
        self.logger.debug("Run script: %s, args: %s" % (str(script), str(args)))
        return self.EM.run_script(script, args, path)

    @expose
    def end_config(self, module):
        self.logger.debug("Set %s as configured" % str(module))
        c = self.conn.cursor()
        c.execute('select * from module where name=?', (module,))
        if not c.fetchone():
            c.execute('insert into module values (?,?)', (module, datetime.now()))
        else:
            c.execute('update module set configured=? where name=?', (datetime.now(), module))
        self.conn.commit()
        c.close()
        return 0
        
    @expose
    def get_state(self, name, module="agent"):
        """ return execution output """
        code, output = self.EM.get_state(name)
        # format output
        tmp = output.data.splitlines()
        output = []
        for line in tmp:
            try:
                if int(line[0]) in range(9):
                    text_code = line[0]
                    text = u""
                    # split by # for multiple translations
                    tmp = line[1:].decode().split('#')
                    for t in tmp:
                        text += _(t, module)
                else:
                    text_code = 0
                    text = line
            # no code at line start
            except ValueError:
                text_code = 0
                text = line
                output.append((text_code, text))
            # no char in line
            except IndexError:
                pass
            else:
                output.append((text_code, text))
                
        return (code, output)

    @expose
    def get_status(self):
        """ return current agent status """
        status = ""
        statuses = self.EM.get_status()
        for sts in statuses:
            status += _(sts, "agent")+', '
        return status[:-2]

class Module:
    """
    Base class for all modules instances

    """

    def __init__(self, path, TM):
        self.TM = TM
        self.logger = logging.getLogger()
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
            self.logger.error("Can't load module %s __init__.py :" % self.id)
            self.logger.error("%s" % err)

    def load(self):
        """ load module basic infos """
        # get common info
        self.id = self.root.attrib.get("id")
        self.TM.set_catalog(self.id, self.path)
        self._name = self.root.findtext("name")
        self._desc = self.root.findtext("desc")
        self._url = self.root.findtext("more/url")
        self._buy = self.root.findtext("more/buy")        
        # get module deps
        self._deps = [m.text for m in self.root.findall("deps/module")]
        # get module conflicts
        self._conflicts = [m.text for m in self.root.findall("conflicts/module")]        
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

    def get_url(self):
        return self._url
    url = property(get_url)

    def get_buy(self):
        return self._buy
    buy = property(get_buy)

    def get_deps(self):
        return self._deps
    deps = property(get_deps)

    def get_conflicts(self):
        return self._conflicts
    conflicts = property(get_conflicts)

    def get_preinst(self):
        return _(self._preinst, self.id).strip()
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
        reload(self.module)
        # get current module config
        try:
            current_config = getattr(self.module, 'get_current_config')()
        except AttributeError:
            current_config = {}
        except Exception, err:
            self.logger.error("Error in get_current_config in %s module : " % self.id)
            self.logger.error(str(err))
            self.logger.error("Can't get module current config")
            current_config = {}
        # get script name and args order
        try:
            script, args = getattr(self.module, 'get_config_info')()
        except AttributeError:
            script, args = (None, [])

        # reset config
        self.config = []
        # no config script we skip the configuration
        if not script:
            self.config.append({'id': self.id, 'skip_config': True, 'do_config': False})
        # we have a config script
        else:
            self.config.append({'id': self.id, 'skip_config': False, 'do_config': False})
            # get XML config
            fields = self.root.findall("config/*")
            if fields:
                # if we have fields, show the configuration page
                self.config[0]['do_config'] = True
            for field in fields:
                field_config = field.attrib
                field_help = field.findtext("help")
                field_label = field.findtext("label")
                field_config["id"] = self.id
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
                # get default value for multi fields
                if "multi" in field_config and "default" in field_config:
                    if type(field_config["default"]) == str:
                        default = field_config["default"].split(";")
                        field_config["default"] = default
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

            if field_name:
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
                # handle multi text fields
                elif "multi" in field:
                    field_value = []
                    for user_field, user_value in user_config.items():
                        f = re.match("^"+self.id+"_"+field_name+"_([0-9]?)_field$", user_field)
                        if f:
                            nb = f.group(1)
                            value = user_config.get(self.id+"_"+field_name+"_"+nb+"_field")
                            field_value.append(value)
                # set values for text,password,options fields
                else:
                    field_value = user_config.get(self.id+"_"+field_name)

                # set default value
                field["default"] = field_value

                # check if field is not empty
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

                # validate field data
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
                if arg == field.get('name'):
                    # network field values
                    if field.get("type") == "network":
                        value = ''
                        for ip, mask in field['default']:
                            network = ip+"/"+mask
                            if field.get("format") == "long":
                                network = str(IP(network))
                            else:
                                network = str(IP(network, make_net=True))
                            value += network+" "
                        value = value[:-1]
                        args_values.append(value)
                    # multi text field
                    elif "multi" in field:
                        value = ''
                        for text in field.get('default'):
                            value += text+" "
                        value = value[:-1]
                        args_values.append(value)
                    # other fields
                    else:
                        args_values.append(field.get('default'))

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

    def network(self, networks):
        for ip, mask in networks:
            if not re.match('^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$', ip):
                return _("Incorrect IP address.", "agent")
            if not mask == "false":
                if not re.match('^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$', mask):
                    return _("Incorrect netmask address.", "agent")
        return None

    def ip(self, ips):
        for ip in ips:
            if not re.match('^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$', ip):
                return _("Incorrect IP address.", "agent")
        return None
