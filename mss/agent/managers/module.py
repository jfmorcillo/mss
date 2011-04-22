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
import logging.handlers
import platform
import sqlite3
from datetime import datetime
from sets import Set

from mss.agent.lib.utils import grep
from mss.agent.classes.module import Module

LOG_FILENAME = '/var/log/mss/mss-agent.log'
logging.basicConfig(level=logging.INFO, filename=LOG_FILENAME)
logger = logging.getLogger('MyLogger')
handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=10485760, backupCount=5)
logger.addHandler(handler)
os.chmod(LOG_FILENAME, 0600)

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

    def __init__(self, PM, TM):
        if platform.machine() == 'x86_64':
            self.arch = 'x86_64'
        else:
            self.arch = 'i586'
        self.modulesDirectory = os.path.join(os.path.dirname(__file__), "..", "modules")
        self.modules = {}
        self.packages = []
        # BDD access
        self.conn = sqlite3.connect('/var/lib/mss/mss-agent.db')
        # translation manager
        self.TM = TM
        self.TM.set_catalog('agent', os.path.join(os.path.dirname(__file__), '..'))
        global _
        _ = self.TM.translate
        # process manager
        self.PM = PM
        # logging
        self.logger = logging.getLogger()
        self.load_packages()
        self.PM.update_medias()
        self.load_modules()

    @expose
    def set_lang(self, lang):
        """ change lang during execution """
        self.logger.info("Lang changed to %s" % lang)
        self.TM.set_lang(lang)

    @expose
    def load_packages(self):
        self.logger.info("Load packages...")
        self.PM.load_packages(self.set_packages)

    @expose
    def check_net(self):
        self.PM.check_net()

    @expose
    def update_medias(self):
        self.PM.update_medias()

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
    def check_media(self, search):
        """ check if media exist """
        return grep(search, '/etc/urpmi/urpmi.cfg')

    def load_modules(self):
        """
        Load all modules at start up
        """
        sys.path.append(self.modulesDirectory)
        modules = self.get_available_modules()
        self.logger.info("Get available mss modules : ")
        for module in modules:
            self.logger.debug("Loading %s" % module)
            m = Module(os.path.join(self.modulesDirectory, module), self.TM, self.arch)
            self.modules[m.id] = m
            self.logger.info(m)

    def get_available_modules(self):
        ret = []
        for item in glob.glob(os.path.join(self.modulesDirectory,
            "*", "__init__.py")):
            ret.append(item.split("/")[-2])
        return ret

    def is_installed(self, module):
        """ check if module is installed """
        packages = set(module.get_packages())
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
        for m in module.conflicts:
            m = self.modules[m]
            if not m in conflicts and m.configured:
                conflicts.append(m)
                self.logger.debug("Conflict with : %s" % str(m.id))
                conflicts = self.get_conflicts(conflicts, m)
        for m in module.deps:
            m = self.modules[m]
            for m1 in m.conflicts:
                m1 = self.modules[m1]
                if not m1 in conflicts and m1.configured:
                    conflicts.append(m1)
                    self.logger.debug("Conflict with : %s" % str(m1.id))
        return conflicts

    def get_module(self, m):
        """ return basic info for one module """
        module = self.modules[m]
        self.is_installed(module)
        # get current conflicts for module
        conflicts = self.get_conflicts([], module)
        conflicts = [conflict.name for conflict in conflicts]
        # return result
        result = {'id': module.id, 'name': module.name,
            'desc': module.desc, 'infos': module.infos,
            'preinst': module.preinst, 'installed': module.installed,
            'configured': module.configured, 'conflict': conflicts,
            'conflicts': module.conflicts, 'deps': module.deps}
        self.logger.debug("Module info : %s" % str(result))
        return result

    @expose
    def get_modules(self, modules):
        """ return basic info for modules """
        self.logger.info("Get modules info : %s" % str(modules))
        result = []
        for m in modules:
            if m in self.modules:
                self.logger.debug("Get module info : %s" % str(m))
                result.append(self.get_module(m))
        return result

    @expose
    def get_packages(self, module):
        """ returns package list for module """
        return self.modules[module].get_packages()

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
                    self.logger.error("Module %s doesn't exists !" % dep)
            return deps
        return None

    @expose
    def get_medias(self, modules):
        """ get medias for modules """
        self.logger.info("Get medias for modules : %s" % str(modules))
        medias = [ self.modules[module].get_medias() for module in modules if not self.check_media(module) and self.modules[module].get_medias() ]
        self.logger.debug("Media list : %s" % str(medias))
        return medias

    @expose
    def add_media(self, module, login=None, passwd=None):
        """ add all medias for module """
        media = self.modules[module].get_medias()
        self.logger.info("Add media : %s" % media.name)
        # get add commands for media
        command = media.get_command(login, passwd)
        self.logger.debug("Execute: %s" % str(command))
        self.PM.add_media(command)

    @expose
    def install_modules(self, modules):
        """ install modules packages """
        self.logger.info("Install modules : %s" % str(modules))
        packages = []
        for module in modules:
            packages += self.modules[module].get_packages()
        if packages:
            self.logger.debug("Install packages : %s" % str(packages))
            self.PM.install_packages(packages)
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
        return self.PM.run_script(script, args, path)

    @expose
    def end_config(self, module):
        self.logger.debug("Set %s as configured" % str(module))
        self.modules[module].configured = True
        return 0

    def clean_output(self, string):
        # remove ANSI codes
        string = re.sub('\x1b[^m]*m', '', string)
        return string

    @expose
    def get_state(self, name, module="agent"):
        """ return execution output """
        code, output = self.PM.p_state(name)
        # format output
        tmp = output.splitlines()
        output = []
    	if tmp:
            for line in tmp:
                try:
                    if int(line[0]) in range(9):
                        text_code = line[0]
                        text = u""
                        # split by # for multiple translations
                        tmp = line[1:].split('#')
                        for t in tmp:
                            text += _(t, module)
                    else:
                        text_code = 0
                        text = self.clean_output(line)
                # no code at line start
                except ValueError:
                    text_code = 0
                    text = line
                    output.append({'code': text_code, 'text': self.clean_output(text)})
                # no char in line
                except IndexError:
                    pass
                else:
                    output.append({'code': text_code, 'text': self.clean_output(text)})
        else:
            code = 2000
            output = [{'code': 0, 'text': u''}]

        self.logger.debug(output)
        return (code, output)

    @expose
    def get_status(self):
        """ return current agent status """
        status = ""
        statuses = self.PM.pm_state()
        for sts in statuses:
            status += _(sts, "agent")+', '
        return status[:-2]

