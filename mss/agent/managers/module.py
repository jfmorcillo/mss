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
import copy
import re
import glob
import sys
import logging
import platform
import traceback
import json
import ConfigParser
import urllib
import urllib2
import time

from mss.agent.lib.utils import Singleton
from mss.agent.lib.db import Session, OptionTable, LogTypeTable, LogTable, ModuleTable
from mss.agent.managers.process import ProcessManager
from mss.agent.managers.translation import TranslationManager

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

    def __init__(self, config_path):
        if platform.machine() == 'x86_64':
            self.arch = 'x86_64'
        else:
            self.arch = 'i586'
        self.config = ConfigParser.ConfigParser();
        try:
            self.config.readfp(open(config_path))
        except OSError:
            logger.exception("Error while reading configuration at %s" % config_path)

        self._token = False
        self.modules = {}
        self.sections_modules = {}
        self.sections = {}
        self.packages = []

        # BDD access
        self.session = Session()
        # Get machine-id
        machine_id = open('/etc/machine-id', 'r').read().strip()
        logger.info("Machine id is %s" % machine_id)
        self.set_option("machine-id", machine_id)
        # Translation manager
        TranslationManager().set_catalog('agent', os.path.join(os.path.dirname(__file__), '..'))
        # Load packages
        self.load_packages()

    @expose
    def load(self):
        """ Load data in the agent """
        self.modules = {}
        self.sections_modules = {}
        self.sections = {}

        self.load_sections()
        logger.debug("Sections loaded.")
        self.load_modules()
        logger.debug("Modules loaded.")

    def setup_python_path(self, local=False):
        """
        Setup the python path to load modules
        """
        local_path = self.config.get("local", "localDir")
        cache_path = self.config.get("local", "cacheDir")
        if local:
            try:
                sys.path.remove(cache_path)
            except ValueError:
                pass
            sys.path.append(local_path)
        else:
            try:
                sys.path.remove(local_path)
            except ValueError:
                pass
            sys.path.append(cache_path)

    def load_modules(self):
        """ load modules """
        if not self._token:
            logger.debug("Using local modules")
            modules_list = self.get_local_modules()
        else:
            logger.debug("Using API modules")
            modules_list = self.get_api_modules()

        from mss.agent.classes.module import Module

        for module_desc in modules_list:
            if "module" in module_desc:
                if not "path" in module_desc["module"]:
                    module_desc["module"]["path"] = os.path.join(self.config.get("local", "cacheDir"),
                                                                 module_desc["slug"])
                self.modules[module_desc['slug']] = Module(module_desc)
                section = self.modules[module_desc['slug']].section
                if not section in self.sections_modules:
                    self.sections_modules[section] = []
                self.sections_modules[section].append(module_desc["slug"])

    def get_local_modules(self):
        paths = []
        result = []

        for item in glob.glob(os.path.join(self.config.get("local", "localDir"),
                                           "*", "__init__.py")):
            module = item.split("/")[-2]
            path = os.path.join(self.config.get("local", "localDir"), module)
            paths.append(path)

        for path in paths:
            try:
                h = open(os.path.join(path, "desc.json"))
                desc = json.load(h)
            except (ValueError, IOError) as e:
                logger.error("Failed to load %s: %s" % (path, str(e)))
            else:
                if not "module" in desc:
                    desc["module"] = {}
                desc["module"]["path"] = path
                result.append(desc)
            finally:
                h.close()

        self.setup_python_path(local=True)

        return result

    def get_api_modules(self):
        """ return list of modules from the API """
        cache_path = os.path.join(self.config.get("local", "cacheDir"), "addons.json")

        try:
            mtime = os.path.getmtime(cache_path)
        except OSError:
            mtime = 0
        # Cache 6 hours
        if int(time.time()) - mtime > self.config.getint("local", "cache"):
            logger.debug("Getting new version of %s" % cache_path)

            result, code = self.request(self.config.get("api", "addonsUrl"))
            if code == 200:
                h = open(cache_path, "w")
                json.dump(result, h)
                h.close()
                h = open(cache_path)
                modules_list = json.load(h)
                h.close()
                self.setup_python_path(local=False)
            else:
                logger.error("Failed to retrieve modules from the API.")
                logger.error("Using local modules.")
                modules_list = self.get_local_modules()
        else:
            h = open(cache_path)
            modules_list = json.load(h)
            h.close()
            self.setup_python_path(local=False)

        return modules_list

    def load_sections(self):
        """ load sections """
        if not self._token:
            logger.debug("Using local sections")
            sections = self.get_local_sections()
        else:
            logger.debug("Using API sections")
            sections = self.get_api_sections()
        self.sections = sections

    def get_local_sections(self):
        """ return local section list """
        path = os.path.join(self.config.get("local", "localDir"), "sections.json")
        h = open(path)
        sections = json.load(h)
        h.close()

        return sections

    def get_api_sections(self):
        """ return section list from API """
        cache_path = os.path.join(self.config.get("local", "cacheDir"), "sections.json")

        try:
            mtime = os.path.getmtime(cache_path)
        except OSError:
            mtime = 0
        # Cache 6 hours
        if int(time.time()) - mtime > self.config.getint("local", "cache"):
            logger.debug("Getting new version of %s" % cache_path)

            result, code = self.request(self.config.get("api", "sectionsUrl"))
            if code == 200:
                h = open(cache_path, "w")
                json.dump(result, h)
                h.close()
                h = open(cache_path)
                sections = json.load(h)
                h.close()
            else:
                logger.error("Failed to retrieve sections from the API.")
                logger.error("Using local sections.")
                sections = self.get_local_sections()
        else:
            h = open(cache_path)
            sections = json.load(h)
            h.close()

        return sections

    @expose
    def set_lang(self, lang):
        """ change lang during execution """
        TranslationManager().set_lang(lang)

    @expose
    def get_lang(self):
        """ return current language """
        return TranslationManager().get_lang()

    @expose
    def set_option(self, slug, value):
        """ add an option in the DB """
        option = OptionTable(slug, value)
        self.session.merge(option)
        self.session.commit()
        return value

    @expose
    def get_option(self, slug):
        """ get an option from the BDD """
        logger.debug("Get option %s" % slug)
        option = self.session.query(OptionTable).get(slug)
        if option:
            result = json.loads(option.value)
        else:
            result = False
        logger.debug("Result: %s" % result)
        return result

    @expose
    def load_packages(self):
        logger.info("Load packages...")
        ProcessManager().load_packages(self.set_packages)

    def set_packages(self, module, code, output):
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
    def check_net(self):
        ProcessManager().check_net()

    @expose
    def update_medias(self):
        ProcessManager().update_medias()

    @expose
    def reboot(self):
        ProcessManager().reboot()

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

    @expose
    def get_modules(self):
        """ return all available modules details """
        logger.info("Get all available modules")
        result = [module.details for slug, module in self.modules.items()]
        logger.debug("Result: %s" % str(result))
        return result

    @expose
    def get_modules_details(self, modules):
        """ return modules info """
        logger.info("Get modules details: %s" % str(modules))
        result = [self.modules[slug].details for slug in modules if slug in self.modules]
        logger.debug("Result: %s" % str(result))
        return result

    @expose
    def get_module_details(self, module):
        """ return module info """
        logger.info("Get module detail: %s" % module)
        if module in self.modules:
            result = self.modules[module].details
        else:
            result = {}
        logger.debug("Result: %s" % str(result))
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
        # force module re-installation
        # (not-used for now)
        #force_modules = []
        #for m in modules:
            #if m.startswith("force-"):
                #force_modules.append(m.replace("force-", ""))
        #modules = [m.replace("force-", "") for m in modules]

        logger.info("Pre-install modules: %s" % ", ".join(modules))
        # store old modules list
        old = modules
        # get dependencies for modules
        modules = self.check_dependencies(modules, [])
        modules = self.order_dependencies(modules)
        # get difference for dep list
        deps = list(set(modules).difference(old))
        # get modules info (modules + dependencies)
        modules = self.get_modules_details(modules)
        # remove already configured modules
        modules = [m for m in modules if not m['configured']]
        # tell if the module is an dependency of selected modules
        for m in modules:
            if m['slug'] in deps:
                m['dep'] = True
            else:
                m['dep'] = False
        logger.debug("Result: %s" % modules)
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
        if module in self.modules:
            return [d for d in self.modules[module].dependencies if d in self.modules]
        return []

    @expose
    def download_modules(self, modules):
        """ download modules from the API """
        for module in modules:
            self.download_module(module)

    @expose
    def download_module(self, module):
        logger.debug("Download module: %s" % module)
        self.modules[module].download()

    @expose
    def get_repositories(self, modules):
        """ get repositories for modules """
        logger.debug("Get packages repositories for modules: %s" % ", ".join(modules))
        repositories = []
        for module in modules:
            repositories = repositories + self.modules[module].repositories
        logger.debug("Result: %s" % repositories)
        return repositories

    @expose
    def add_repository(self, module_slug, repo_slug, login=None, passwd=None):
        """ add repository of a module """
        repositories = self.modules[module_slug].repositories
        for repository in repositories:
            if repository.slug == repo_slug:
                logger.info("Add repository: %s" % repository.name)
                ProcessManager().add_repository(repository.get_command(login, passwd))

    @expose
    def install_modules(self, modules):
        """ install modules packages """
        logger.info("Install modules: %s" % str(modules))
        packages = []
        for module in modules:
            packages += self.modules[module].packages
        if packages:
            logger.debug("Install packages: %s" % str(packages))
            ProcessManager().install_packages(packages)
            return True
        else:
            logger.info("No packages to install")
            return False

    @expose
    def get_config(self, modules):
        """ get modules config """
        logger.info("Get config for modules: %s" % ", ".join(modules))
        config = []
        for module in modules:
            config.append(self.modules[module].get_config())
        logger.debug("Result: %s" % str(config))
        return config

    @expose
    def valid_config(self, modules, modules_config):
        """ validate user configuration for modules """
        logger.info("Valid config for modules: %s" % ", ".join(modules))
        config = []
        errors = False
        for module in modules:
            module_errors, module_config = self.modules[module].valid_config(modules_config)
            config.append(module_config)
            if module_errors:
                errors = True
        logger.debug("Result: (%s, %s)" % (errors, str(config)))
        return (errors, config)

    @expose
    def run_config(self, module):
        """ run configuration for module """
        logger.debug("Run configuration for %s" % str(module))
        path, script, args = self.modules[module].info_config()
        logger.debug("Run script: %s, args: %s" % (str(script), str(args)))
        logger.debug("Path is: %s" % path)
        return ProcessManager().run_script(script, args, path, module, self.end_config)

    @expose
    def end_config(self, module, code, output):
        """
        Callback after run script
        """
        if code == 0 and not self.modules[module].configured:
            logger.debug("Set %s as configured" % str(module))
            self.modules[module].configured = True
            # try to store the config log
            try:
                log_type = self.session.query(LogTypeTable).filter(LogTypeTable.name == "config").first()
                if not log_type:
                    log_type = LogTypeTable("config")
                    self.session.add(log_type)
                    self.session.commit()
                module_obj = self.session.query(ModuleTable).filter(ModuleTable.name == module).first()
                config_log = LogTable(log_type.id, module_obj.id, self.get_state("config", module))
                logger.debug("Saving %s configuration log in the DB" % str(module))
                self.session.add(config_log)
                self.session.commit()
            except:
                pass
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
        if not tmp:
            output = [{'code': 0, 'text': u''}]
        else:
            output = []
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

        logger.debug("Get state: %s - %s" % (code, output))
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
        sections = copy.deepcopy(self.sections)
        for section in sections:
            section["name"] = _(section["name"], "agent")
        return sections

    @expose
    def get_section(self, section):
        """ return modules belonging to section
            organized by category
        """
        logger.info("Getting section %s modules" % section)
        result = []
        if section in self.sections_modules:
            modules_list = self.sections_modules[section]
            for module_slug in modules_list:
                if self.modules[module_slug].standalone:
                    category = self.modules[module_slug].category
                    details = self.modules[module_slug].details
                    exist = False
                    for cat in result:
                        if category["slug"] == cat["slug"]:
                            exist = True
                            break
                    if not exist:
                        result.append(category)
                    for i, cat in enumerate(result[:]):
                        if category["slug"] == cat["slug"]:
                            if not "modules" in cat:
                                result[i]["modules"] = []
                            result[i]["modules"].append(details)
                            break
            logger.debug("Result: %s" % str(result))
        return result

    @expose
    def authenticate(self, user, password):
        """ Authenticate mss-www to the agent """
        self._token = False
        if not user or not password:
            return False
        # Local auth with PAM
        if user == "root":
            logger.debug("PAM authentication")
            from mss.agent.lib import pam
            result = pam.authenticate(user, password, service="passwd")
            if result:
                logger.debug("Logged with PAM.")
            return result
        # API auth
        else:
            logger.debug("ServicePlace authentication")
            url = self.config.get("api", "tokenUrl")
            result, code = self.request(url, {'username': user, 'password': password})
            if code == 200:
                if 'token' in result:
                    self._token = result['token']
                    logger.debug("Logged with the ServicePlace !")
                    return True
            logger.error("Login failed against the ServicePlace.")
            return False

    def request(self, url, params=None):
        """
        Used to query the ServicePlace API

        Handles token and language headers
        """
        code = 500
        if params:
            params = urllib.urlencode(params)
        request = urllib2.Request(url, params)
        if self._token:
            request.add_header('Authorization', 'Token ' + self._token)
        request.add_header('Accept-Language', TranslationManager().get_lang().split('_')[0] + ',en')
        try:
            response = urllib2.urlopen(request)
            if response.info().gettype() == "application/json":
                result = json.loads(response.read())
            else:
                result = response.read()
            code = response.getcode()
        except urllib2.HTTPError as e:
            result = "HTTP Error:" + str(e.reason) + " " + url
            logger.error(result)
            code = e.code
        except urllib2.URLError as e:
            result = "URL Error:" + str(e.reason) + " " + url
            logger.error(result)

        logger.debug("Return code %s" % code)
        return (result, code)
