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
from glob import glob
from gettext import gettext as _

from mss.agent.lib.utils import Singleton
from mss.agent.classes.process import ProcessThread
from mss.agent.classes.request import RequestThread
from mss.agent.managers.translation import TranslationManager

logger = logging.getLogger(__name__)


class ProcessManager:
    """ Class managing running tasks """
    __metaclass__ = Singleton

    def __init__(self):
        # thread pool
        self.threads = []

    def load_packages(self, callback):
        """ get all installed packages """
        self.launch("load", _("Loading packages list"),
                    ["rpm", "-qa", "--queryformat", "%{NAME}#"],
                    callback=callback)

    def install_packages(self, packages):
        """ launch installation of packages list """
        for cdrom in glob("/dev/disk/by-label/Mandriva*"):
            m = self.launch("mount-cdrom",
                            _('Mounting packages medium'),
                            ["mount", cdrom, "/run/mss/urpmi-medium"])
            m.join()
            if m.process.returncode == 0:
                break

        self.launch("install",
                    _('Installing packages...'),
                    ["urpmi", "--auto", "--no-suggests"] + packages)

    def unmount_medias(self):
        self.launch("umount-urpmi-medium",
                    _('Unmounting packages medium'),
                    ["umount", "/run/mss/urpmi-medium"])

    def run_script(self, script, args, cwd, module, callback):
        """ launch configuration script for module """
        env = {'TEXTDOMAIN': module,
               'TEXTDOMAINDIR': os.path.join(TranslationManager().get_catalog_path(module), 'locale')}
        if os.path.exists(os.path.join(cwd, script)):
            self.launch("config",
                        _("Running configuration"),
                        ["bash", script] + args, cwd=cwd,
                        module=module, env=env, callback=callback)
            return True
        else:
            return False

    def reboot(self):
        """ reboot the server """
        self.launch("reboot",
                    _('Rebooting...'),
                    "sleep 3 && reboot", shell=True)

    def update_medias(self):
        """ update medias lists """
        self.launch("update",
                    _('Updating medias'),
                    ["urpmi.update", "-a"])

    def check_net(self):
        """ check if net is available """
        self.launch("net",
                    _('Checking network'),
                    ["wget", "-T", "2", "http://api.mandriva.com", "-O", "/dev/null"], replace=True, env={'LC_ALL': 'C'})

    def add_repository(self, command):
        """ add repository """
        self.launch("repository", _("Adding media"), command)

    def download_module(self, url, params=None, headers=None, module=None, callback=None):
        """ download module """
        if module:
            status = _("Downloading %s addon..." % module)
        else:
            status = _("Downloading addon...")
        self.request("download_module", status, url, params, headers, callback=callback, replace=True)

    def launch(self, type, status, command, cwd=None, callback=None, shell=False,
               replace=False, env=None, module="agent"):
        """ wrapper to run non blocking shell commands """
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
            if 'LC_ALL' not in env:
                env['LC_ALL'] = TranslationManager().locale_name
            thread = ProcessThread(type, status, module, command, cwd, callback, shell, env)
            self.threads.append(thread)
            logger.debug("Create %s thread for module %s" % (type, module))
            logger.debug("Command is: %s" % " ".join(command))
            thread.start()
        else:
            # let the thread finish
            pass

        return thread

    def request(self, type, status, url, params=None, headers=None,
                callback=None, module="agent", replace=False):
        """ wrapper to make non blocking http requests """
        thread = self.get_thread(type, module)
        # stop the current thread if replace is True
        if replace and thread:
            thread.stop()
            logger.debug("Stopping %s thread of module %s" % (type, module))
        if not thread or not thread.isAlive():
            # remove previoud thread
            if thread:
                self.threads.remove(thread)
            thread = RequestThread(type, status, module, url, params, headers, callback)
            self.threads.append(thread)
            logger.debug("Create %s thread for module %s" % (type, module))
            logger.debug("URL: %s" % url)
            logger.debug("Headers: %s" % str(headers))
            logger.debug("Params: %s" % str(params))
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
        else:
            raise Exception("No process found for %s %s" % (module, type))

    def pm_state(self):
        """ get execution manager status """
        status = []
        for thread in self.threads:
            if thread.isAlive():
                status.append(thread.status)
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
