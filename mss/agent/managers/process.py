# -*- coding: UTF-8 -*-
#
# (c) 2010-2012 Mandriva, http://www.mandriva.com/
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
import logging
from gettext import gettext as _

from mss.agent.lib.utils import Singleton
from mss.agent.classes.process import ProcessThread
from mss.agent.manager.translation import TranslationManager

logger = logging.getLogger(__name__)


class ProcessManager:
    """ Class managing running tasks """
    __metaclass__ = Singleton

    def __init__(self):
        # thread pool
        self.threads = []

    def load_packages(self, callback):
        """ get all installed packages """
        self.launch("load", ["rpm", "-qa", "--queryformat", "%{NAME}#"],
                    callback=callback)

    def install_packages(self, packages):
        """ launch installation of packages list """
        self.launch("install", ["urpmi", "--auto", "--no-suggests"] + packages)

    def run_script(self, script, args, cwd, module):
        """ launch configuration script for module """
        env = {'TEXTDOMAIN': module,
               'TEXTDOMAINDIR': os.path.join(TranslationManager.get_catalog(module), 'locale')}
        if os.path.exists(os.path.join(cwd, script)):
            self.launch("config", ["bash", script] + args, cwd=cwd,
                        module=module, env=env)
            return True
        else:
            return False

    def reboot(self):
        """ reboot the server """
        self.launch("reboot", "sleep 3 && reboot", shell=True)

    def update_medias(self):
        """ update medias lists """
        self.launch("update", ["urpmi.update", "-a"])

    def check_net(self):
        """ check if net is available """
        self.launch("net", ["wget", "-T", "2", "http://api.mandriva.com", "-O", "/dev/null"], replace=True, env={'LC_ALL': 'C'})

    def add_media(self, command):
        """ add media """
        self.launch("media", command, shell=True)
        #return (self.threads['media'].code, self.threads['media'].output)

    def launch(self, type, command, cwd=None, callback=None, shell=False,
               replace=False, env=None, module="agent"):
        """ launch wrapper """
        thread = self.get_thread(type, module)
        # stop the current thread if replace is True
        if replace and thread:
            thread.stop()
            logger.debug("Stopping %s thread of module %s" % (type, module))
        if not thread or not thread.isAlive():
            # remove previoud thread
            if thread:
                self.threads.remove(thread)
            if not env:
                env = {}
            if not 'LC_ALL' in env:
                env['LC_ALL'] = TranslationManager().lang
            thread = ProcessThread(type, module, command, cwd, callback, shell, env)
            self.threads.append(thread)
            logger.debug("Create %s thread for module %s" % (type, module))
            logger.debug("Command is: %s" % " ".join(command))
            thread.start()
        else:
            # let the thread finish
            pass

    def get_thread(self, type, module="agent"):
        """ get thread in list """
        for thread in self.threads:
            if thread.type == type and thread.module == module:
                return thread
        return False

    def p_state(self, type, module="agent"):
        """ get thread execution state """
        thread = self.get_thread(type, module)
        if thread:
            return (thread.code, thread.output)

    def pm_state(self):
        """ get execution manager status """
        status = []
        for thread in self.threads:
            if thread.isAlive():
                if thread.type == "load":
                    status.append(_("Loading packages list"))
                if thread.type == "install":
                    status.append(_("Installing packages"))
                if thread.type == "update":
                    status.append(_("Updating medias"))
                if thread.type == "media":
                    status.append(_("Adding media"))
                if thread.type == "config":
                    status.append(_("Running configuration"))
                if thread.type == "net":
                    status.append(_("Checking network"))
                if thread.type == "reboot":
                    status.append(_("Rebooting"))
        if not status:
            status.append(_("Ready"))
        return status


class ProcessManagerError(Exception):
    """Base class for exceptions in ExecManager."""

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class ProcessManagerBusyError(ProcessManagerError):
    pass


class ProcessManagerStateDoesntExists(ProcessManagerError):
    pass
