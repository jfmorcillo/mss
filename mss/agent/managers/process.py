# -*- coding: UTF-8 -*-
#
# (c) 2010 Mandriva, http://www.mandriva.com/
#
# $Id$
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
from gettext import gettext as _

from mss.agent.classes.process import ProcessThread


class ProcessManager:
    """ Class managing running tasks """

    def _dispatch(self, method, params):
        func = getattr(self, method)
        if not is_exposed(func):
            raise Exception('Method "%s" is not supported' % method)

        return func(*params)

    def __init__(self):
        # thread pool
        self.threads = {}

    def load_packages(self, callback):
        """ get all installed packages """
        self.launch("load", ["rpm", "-qa", "--queryformat", "%{NAME}#"],
            callback=callback)

    def install_packages(self, packages):
        """ launch installation of packages list """
        self.launch("install", ["urpmi", "--auto", "--force"] + packages)

    def run_script(self, script, args, cwd):
        """ launch configuration script for module """
        if os.path.exists(os.path.join(cwd, script)):
            self.launch("config", ["bash", script] + args, cwd=cwd)
            return True
        else:
            return False

    def update_medias(self):
        """ update medias lists """
        self.launch("update", ["urpmi.update", "-a"])

    def check_net(self):
        """ check if net is available """
        self.launch("net", ["ping", "-c", "2", "my.mandriva.com"], replace=True)

    def add_media(self, command):
        """ add media """
        self.launch("media", command, shell=True)
        #return (self.threads['media'].code, self.threads['media'].output)

    def launch(self, name, command, wait=False, cwd=None, callback=None, shell=False, replace=False):
        """ launch wrapper """
        # stop the current thread if replace if True
        # if replace and name in self.threads:
        #    self.threads[name].stop()
        # accept only one thread
        if not name in self.threads or not self.threads[name].isAlive():
            self.threads[name] = ProcessThread(command, cwd, callback, shell)
            self.threads[name].start()
            if wait:
                self.threads[name].join()
        else:
            raise ProcessManagerBusyError, "ProcessManager is busy"

    def p_state(self, name):
        """ get thread execution state """
        if name in self.threads:
            return (self.threads[name].code, self.threads[name].output)

    def pm_state(self):
        """ get execution manager status """
        status = []
        for name, thread in self.threads.items():
            if thread.isAlive():
                if name == "load":
                    status.append(_("Loading packages list"))
                if name == "install":
                    status.append(_("Installing packages"))
                if name == "update":
                    status.append(_("Updating medias"))
                if name == "media":
                    status.append(_("Adding media"))
                if name == "config":
                    status.append(_("Running configuration"))
                if name == "net":
                    status.append(_("Checking network"))
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
