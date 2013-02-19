# -*- coding: UTF-8 -*-
#
# (c) 2010 Mandriva, http://www.mandriva.com/
#
# This file is part of Mandriva Server Setup
#
# MSS is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MSS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MSS; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import os
import re
import glob
import sys
import logging
import platform
import traceback
import json
import ConfigParser
import urllib2
import hashlib
import zipfile

from mss.agent.lib.utils import grep, Singleton
from mss.agent.lib.db import Session, OptionTable, LogTypeTable, LogTable, ModuleTable
from mss.agent.classes.module import Module
from mss.agent.managers.process import ProcessManager
from mss.agent.managers.translation import TranslationManager

LSB_FILENAME = '/etc/os-release'
_ = TranslationManager().translate
logger = logging.getLogger(__name__)


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
    __metaclass__ = Singleton

    def _dispatch(self, method, params):
        func = getattr(self, method)
        if not is_exposed(func):
            raise Exception('Method "%s" is not supported' % method)

        try:
            return func(*params)
        except:
            logger.error(traceback.format_exc())
            raise

    def __init__(self):
        if platform.machine() == 'x86_64':
            self.arch = 'x86_64'
        else:
            self.arch = 'i586'
        self.mssAgentConfig = ConfigParser.ConfigParser();
        self.mssAgentConfig.readfp(open("/etc/mss/agent.ini"))
        self.modulesDirectory = self.mssAgentConfig.get("local", "addons")
        logger.warning("Looking for modules inside %s" % self.modulesDirectory)
        self.modules = {}
        self._sections = []
        self._hAddons = {}
        self._addons = []
        self.packages = []
        sel._lang = 'en,fr'

        # translation manager
        TranslationManager().set_catalog('agent', os.path.join(os.path.dirname(__file__), '..'))
        # BDD access
        self.session = Session()
        # logging
        self.load_packages()
        # Get machine-id
        machine_id = open('/etc/machine-id', 'r').read().strip()
        logger.info("Machine id is %s" % machine_id)
        self.set_option("machine-id", machine_id)

    def load_addons(self):
        """ return addons list """
        addons_json_fp = open(os.path.join(self.mssAgentConfig.get("local", "cache"), "addons.json"), "w")
        # Load modules description
        err = False
        status = "OK"
        try:
            req = urllib2.Request(self.mssAgentConfig.get("addons", "url"))
            req.add_header('Authorization', 'Token ' + self._token)
            req.add_header('Accept-Language', self._lang)
            f_addons = urllib2.urlopen(req)
            addons_json_fp.write(f_addons.read())
        except urllib2.HTTPError, e:
            err = True
            status = "HTTP Error: " + str(e.code) + ": " + self.mssAgentConfig.get("addons", "url")
        except urllib2.URLError, e:
            err = True
            status = "URL Error: " + str(e.reason) + ": " + self.mssAgentConfig.get("addons", "url")
        addons_json_fp.close()

        addons_json_fp = open(os.path.join(self.mssAgentConfig.get("local", "cache"), "addons.json"), "r")
        self._addons = json.load(addons_json_fp)
        addons_json_fp.close()

        self._hAddons = {}
        for addon in self._addons:
            self._hAddons[addon["slug"]] = addon

        return (err, status)

    def load_sections(self):
        """ return section list """
        sections_json_fp = open(os.path.join(self.mssAgentConfig.get("local", "cache"), "sections.json"), "w")
        # Load modules description
        err = False
        status = "OK"
        try:
            req = urllib2.Request(self.mssAgentConfig.get("sections", "url"))
            req.add_header('Authorization', 'Token ' + self._token)
            req.add_header('Accept-Language', self._lang)
            f_sections = urllib2.urlopen(req)
            sections_json_fp.write(f_sections.read())
        #handle errors
        except urllib2.HTTPError, e:
            err = True
            status = "HTTP Error: " + str(e.code) + ": " + self.mssAgentConfig.get("sections", "url")
        except urllib2.URLError, e:
            err = True
            status = "URL Error: " + str(e.reason) + ": " + self.mssAgentConfig.get("sections", "url")
        sections_json_fp.close()

        # Load sections
        if not err:
            sections_json_fp = open(os.path.join(self.mssAgentConfig.get("local", "cache"), "sections.json"))
            self._sections = json.load(sections_json_fp)
            sections_json_fp.close()
        return (err, status)

    def load_categories(self):
        """ return categories per section """
        self._categories = {}
        for section in self._sections:
            self._categories[section["slug"]] = [{'slug': 'others', 'name': 'Addons', 'modules': []}]

        self._categories["hidden"] = []
        for addon in self._addons:
            if addon["standalone"]:
                section = addon["module"]["section"]
                if addon["categories"] == []:
                    addon['categories'].append({'slug': 'others', 'name': 'Addons'})
                for category in addon["categories"]:
                    category["modules"] = []
                    notFound = True
                    for cat in self._categories[section]:
                        if cat["slug"] == category["slug"]:
                            notFound = False
                    if notFound:
                        self._categories[section].append(category)

    def load_modules2(self):
        """ Dispatch modules in categories """
        # Add modules to categories
        for addon in self._addons:
            if addon["standalone"]:
                section = addon["module"]["section"]
                if addon["categories"] == []:
                    addon['categories'].append({'slug': 'others', 'name': 'Addons'})
                for category in addon["categories"]:
                    for cat in self._categories[section]:
                        if cat["slug"] == category["slug"]:
                            cat["modules"].append(addon["slug"])
            else:
                self._categories["hidden"].append(addon["slug"])

    @expose
    def load_module(self, module):
        """ Load one module """
        sys.path.append(self.modulesDirectory)
        modules = self.get_available_modules()
        logger.info("Get available mss modules : ")

        if module not in modules:
            self.download_modules([module])
            modules.append(module)

        if module in modules and module not in self.modules:
            logger.debug("Loading %s" % module)
            m = Module(os.path.join(self.modulesDirectory, module), self, self.arch)
            self.modules[m.slug] = m
            logger.info(m)
            for mod in m.dependencies:
                self.load_module(mod)

    @expose
    def load(self):
        """ Load sections/modules after logging successfully """
                # Load section info
        err, status = self.load_sections()
        if not err:
            # Load addon list
            err, status = self.load_addons()
            if not err:
                # Load categories
                self.load_categories()
                self.load_modules2()
        return (err, status)

    @expose
    def set_lang(self, lang):
        """ change lang during execution """
        logger.info("Lang changed to %s" % lang)
        TranslationManager().set_lang(lang)
        if lang == 'fr_FR':
            self._lang = 'fr,en'
        else:
            self._lang = 'en,fr'

    @expose
    def set_option(self, slug, value):
        """ add an option in the DB """
        option = OptionTable(slug, value)
        self.session.merge(option)
        self.session.commit()

    @expose
    def get_option(self, slug):
        """ get an option from the BDD """
        option = self.session.query(OptionTable).get(slug)
        if option:
            return json.loads(option.value)
        else:
            return False

    @expose
    def load_packages(self):
        logger.info("Load packages...")
        ProcessManager().load_packages(self.set_packages)

    @expose
    def check_net(self):
        ProcessManager().check_net()

    @expose
    def update_medias(self):
        ProcessManager().update_medias()

    @expose
    def reboot(self):
        ProcessManager().reboot()

    def set_packages(self, code, output):
        if code == 0:
            packages = output.split('#')
            if not packages:
                logger.error("No packages found.")
            else:
                self.packages = packages
                logger.info("Loading packages done.")
        else:
            logger.error("Can't load packages.")

    @expose
    def check_media(self, search):
        """ check if media exist """
        return grep(search, '/etc/urpmi/urpmi.cfg')

    @expose
    def check_distribution(self, distribution):
        """
        Allow to check which distribution we are using
        """
        if os.path.exists(LSB_FILENAME):
            for line in open(LSB_FILENAME):
                if line.startswith("PRETTY_NAME"):
                    if distribution in line:
                        return True
        return False

    def get_available_modules(self):
        ret = []
        for item in glob.glob(os.path.join(self.modulesDirectory,
                                           "*", "__init__.py")):
            ret.append(item.split("/")[-2])
        return ret

    def check_installed(self, module):
        """ check if module is installed """
        packages = set(module.packages)
        # check if packages are installed
        if len(packages) == len(packages.intersection(self.packages)):
            module.installed = True
            return True
        else:
            module.installed = False
            return False

    def get_conflicts(self, conflicts, module):
        """ return a module list of current conflicts
            with module """
        if module in self.modules:
            module = self.modules[module]
            _conflicts = module.conflicts
            _dependencies = module.dependencies
            _configured = module.configured
        else:
            module = self._hAddons[module]
            _conflicts = module['module'].get('conflicts', [])
            _dependencies = module['module'].get('dependencies', [])
            _configured = module['module'].get('configured', False)
        for m in _conflicts:
            try:
                if not m in conflicts and _configured:
                    conflicts.append(m)
                    logger.debug("Conflict with : %s" % m)
                    conflicts = self.get_conflicts(conflicts, m)
            except KeyError:
                pass
        for m in _dependencies:
            conflicts = self.get_conflicts(conflicts, m)
        return conflicts

    def get_module(self, m):
        """ return basic info for one module """
        if m in self.modules:
            module = self.modules[m]
            self.check_installed(module)
            
            configured = module.configured
            installed = module.installed
            actions = module.actions
        else:
            details = self.get_module_details(m)
            configured = details['configured']
            installed = details['installed']
            actions = details['actions']

        # get current conflicts for module
        conflicts = self.get_conflicts([], m)
        #conflicts = [conflict.name for conflict in conflicts]

        mod = self._hAddons.get(m, {})
        # return result
        result = {
            'slug': mod['slug'], 'name': mod['name'],
            'actions': actions, 'desc': mod.get('description'),
            'purchased': mod.get("purchased", False), 'price': mod.get("price", 0),
            'installed': installed,
            'configured': configured, 'conflict': conflicts,
            'conflicts': mod['module'].get('conflicts', []),
            'dependencies': mod['module'].get('dependencies', []),
            'reboot': mod['module'].get('reboot', False)}
        logger.debug("Module info: %s" % str(result))
        return result

    @expose
    def get_modules(self, modules):
        """ return basic info for modules """
        logger.info("Get modules info: %s" % str(modules))
        result = []
        for m in modules:
            logger.debug("Get module info: %s" % str(m))
            result.append(self.get_module(m))
        return result

    @expose
    def get_packages(self, module):
        """ returns package list for module """
        return self.modules[module].packages

    @expose
    def preinstall_modules(self, modules):
        """
        get dependencies for modules to install
        return modules infos
        """
        self.download_modules(modules)
        
        for module in modules:
            if module not in self.modules:
                self.load_module(module)

        # force module re-installation
        # (not-used for now)
        force_modules = []
        for m in modules:
            if m.startswith("force-"):
                force_modules.append(m.replace("force-", ""))
        modules = [m.replace("force-", "") for m in modules]
        # store old modules list
        old = modules
        # get dependencies for modules
        modules = self.check_dependencies(modules, [])
        modules = self.order_dependencies(modules)
        # get difference for dep list
        deps = list(set(modules).difference(old))
        # get modules info (modules + dependencies)
        modules = self.get_modules(modules)
        # remove already configured modules unless force
        modules = [m for m in modules if not m['configured'] or m['slug'] in force_modules]
        # tell if the module is an dependency of selected modules
        # or if we reinstall it
        for m in modules:
            if m['slug'] in deps:
                m['dep'] = True
            else:
                m['dep'] = False
            if m['slug'] in force_modules:
                m['force'] = True
            else:
                m['force'] = False
        logger.info("Pre-install modules : %s" % str(modules))
        return modules

    def order_dependencies(self, modules, cnt=1):
        for module in modules:
            # if the module has dependencies and is not indexed
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
                # if all dependencies are indexed
                if set_index:
                    module[2] = cnt

        # make 10 pass to determine indexes
        # FIXME! this limits the nb max of the modules list
        if(cnt < 10):
            cnt += 1
            modules = self.order_dependencies(modules, cnt)
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

    def check_dependencies(self, modules, dependencies):
        """ get dependencies for modules
            create a list with the form : [ [ module, [dependencies], index ],... ]
        """
        for module in modules:
            deps = self.get_dependencies(module)
            if deps:
                # set the index a -1 to calculate index
                dependencies.append([module, deps, -1])
                dependencies = self.check_dependencies(deps, dependencies)
            else:
                # set the index at 0 as the module has no dependencies
                dependencies.append([module, None, 0])
        return dependencies

    def get_dependencies(self, module):
        """ get dependencies for module """
        if self._hAddons[module]['module'].get('dependencies', None):
            deps = []
            for dep in self._hAddons[module]['module']['dependencies']:
                try:
                    if self._hAddons[dep]:
                        deps.append(dep)
                except KeyError:
                    logger.error("Module %s doesn't exists !" % dep)
            return deps
        return None

    @expose
    def get_medias(self, modules):
        """ get medias for modules """
        logger.info("Get medias for modules: %s" % str(modules))
        medias = [self._hAddons[module]['repositories'] for module in modules if not self.check_media(module) and self._hAddons[module]['repositories']]
        logger.debug("Repository list: %s" % str(medias))
        return medias

    @expose
    def add_media(self, module, login=None, passwd=None):
        """ add all medias for module """
        media = self.modules[module].medias
        logger.info("Add media : %s" % media.name)
        # get add commands for media
        command = media.get_command(login, passwd)
        logger.debug("Execute: %s" % str(command))
        ProcessManager().add_media(command)

    @expose
    def download_modules(self, modules):
        """ Download modules if not already present on disk """
        logger.info("Download modules : %s" % str(modules))
        for module in modules:
            if not os.path.exists(os.path.join(self.mssAgentConfig.get("local", "addons"), module)):
                logger.info("Download module : %s" % str(module))
                # Download
                f_mod = open(os.path.join("/tmp", module+".zip"), "wb")
                err = False
                status = "OK"
                try:
                    req = urllib2.Request(self._hAddons[module]['module']['file'])
                    req.add_header('Authorization', 'Token ' + self._token)
                    req.add_header('Accept-Language', self._lang)
                    f = urllib2.urlopen(req)
                    f_mod.write(f.read())
                    #handle errors
                except urllib2.HTTPError, e:
                    err = True
                    status = "HTTP Error: " + str(e.code) + ": " + self._hAddons[module]['module']['file']
                except urllib2.URLError, e:
                    err= True
                    status = "URL Error: " + str(e.reason) + ": " + self._hAddons[module]['module']['file']
                f_mod.close()

                # Verify sha1
                logger.info("Unzip module: %s" % os.path.join("/tmp", module+".zip"))
                f_mod = open(os.path.join("/tmp", module+".zip"), "rb")
                sha1 = hashlib.sha1()
                try:
                    sha1.update(f_mod.read())
                finally:
                    f_mod.close()

                logger.info("Process sha1sum: %s" % sha1.hexdigest())
                if sha1.hexdigest() == self._hAddons[module]['module']['file_sha1']:
                    logger.info("Zip file is valid: unzip...")
                    os.mkdir(os.path.join(self.mssAgentConfig.get("local", "addons"), module))
                    zip = zipfile.ZipFile(os.path.join("/tmp", module+".zip"))
                    zip.extractall(path=os.path.join(self.mssAgentConfig.get("local", "addons"), module))
                else:
                    logger.info("Zip file is invalid...")
                    err = True
                    status = "sha1sum invalid"

                return (err, status)

    @expose
    def install_modules(self, modules):
        """ install modules packages """
        logger.info("Install modules : %s" % str(modules))
        packages = []
        for module in modules:
            packages += self.modules[module].packages
        if packages:
            logger.debug("Install packages : %s" % str(packages))
            ProcessManager().install_packages(packages)
            return True
        else:
            logger.info("No packages to install")
            return False

    @expose
    def get_config(self, modules):
        """ get modules config """
        logger.info("Get config for modules : %s" % str(modules))
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
        logger.debug("Run configuration for %s" % str(module))
        path, script, args = self.modules[module].info_config()
        logger.debug("Run script: %s, args: %s" % (str(script), str(args)))
        return ProcessManager().run_script(script, args, path, module)

    @expose
    def end_config(self, module):
        if not self.modules[module].configured:
            logger.debug("Set %s as configured" % str(module))
            self.modules[module].configured = True
            # store the config log
            logger.debug("Saving %s configuration log in the DB" % str(module))
            log_type = self.session.query(LogTypeTable).filter(LogTypeTable.name == "config").first()
            if not log_type:
                log_type = LogTypeTable("config")
                self.session.add(log_type)
                self.session.commit()
            module_obj = self.session.query(ModuleTable).filter(ModuleTable.name == module).first()
            config_log = LogTable(log_type.id, module_obj.id, self.get_state("config", module))
            self.session.add(config_log)
            self.session.commit()
        return 0

    def clean_output(self, string):
        # remove ANSI codes
        string = re.sub('\x1b[^m]*m', '', string)
        return string

    @expose
    def get_state(self, type, module="agent"):
        """ return execution output """
        code, output = ProcessManager().p_state(type, module)
        # format output
        tmp = output.splitlines()
        output = []
        if tmp:
            for line in tmp:
                try:
                    if int(line[0]) in range(9):
                        text_code = line[0]
                        text = line[1:]
                    else:
                        text_code = 0
                        text = line
                    output.append({'code': text_code, 'text': self.clean_output(text)})
                # no code at line start
                except ValueError:
                    text_code = 0
                    text = line
                    output.append({'code': text_code, 'text': self.clean_output(text)})
                # no char in line
                except IndexError:
                    pass
        else:
            code = 2000
            output = [{'code': 0, 'text': u''}]

        return (code, output)

    @expose
    def get_status(self):
        """ return current agent status """
        status = []
        statuses = ProcessManager().pm_state()
        for sts in statuses:
            status.append(_(sts, "agent"))
        return ', '.join(status)

    @expose
    def get_sections(self):
        """ return list of sections """
        return self._sections

    def get_categories(self, section):
        """ return list of categories """
        if section in self._categories:
            return self._categories[section]
        else:
            return []

    @expose
    def get_section(self, section):
        """ return modules belonging to section """
        # Init a section structure to be sent to mss-www view.py
        _section = {}
        _section["slug"] = section
        for sec in self._sections:
            if sec["slug"] == section:
                _section["name"] = sec["name"]
        # Set addons list
        _section["bundles"] = self._categories[section]
        return _section

    @expose
    def get_module_details(self, module):
        """ return the detailed description on a module if it exist """
        mod = self.session.query(ModuleTable).filter(ModuleTable.name == module).first()
        if mod and mod.configured:
            desc_json_fp = open(os.path.join(self.modulesDirectory, module, "desc.json"))
            conf = json.load(desc_json_fp)
            desc_json_fp.close()
            actions = conf.get("actions", [])
            installed = True
            configured = True
        else:
            actions = []
            installed = False
            configured = False
        self._hAddons[module]['module']['installed'] = installed
        self._hAddons[module]['module']['configured'] = configured
        details = {"actions": actions, "installed": installed, "configured": configured}
        return details

    @expose
    def get_authentication_token(self, login, password):
        """ return status of authentication to API """
        data = 'username=' + login + '&password=' + password
        url = self.mssAgentConfig.get("api", "url") + 'token/'
        self._token = ""
        err = False
        status = "OK"
        try:
            result = urllib2.urlopen(url, data)
            info = json.loads(result.read())
            if 'token' in info:
                self._token = info['token']
            elif 'non_field_errors' in info:
                err = True
                status = info['non_field_errors']
            else:
                err = True
                status = "unknown"
        except urllib2.HTTPError, e:
            err = True
            status = "HTTP Error:" + str(e.code) + " " + url
        except urllib2.URLError, e:
            err = True
            status = "URL Error:" + str(e.reason) + " " + url
        return (err, status)
