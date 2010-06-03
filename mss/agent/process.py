#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import select
import threading
import xmlrpclib
from subprocess import Popen, PIPE, STDOUT
import time
from gettext import gettext as _


class ExecManager:
    """ Class managing running tasks """

    def __init__(self):
        # thread pool
        self.threads = {}

    def load_packages(self, callback):
        """ get all installed packages """
        self.launch("load", ["rpm", "-qa", "--queryformat", "%{NAME}#"], 
            callback=callback)

    def install_packages(self, packages):
        """ launch installation of packages list """
        self.launch("install", ["urpmi", "--auto"] + packages)

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
        
    def add_media(self, name, proto, url, login=None, passwd=None):
        """ add media """
        if login and passwd:
            self.launch("media", ["urpmi.addmedia", name,
                proto+"://"+login+":"+passwd+"@"+url], wait=True)
        else:
            self.launch("media", ["urpmi.addmedia", name,
                proto+"://"+url], wait=True)
        return (self.threads['media'].code, self.threads['media'].output)

    def launch(self, name, command, wait=False, cwd=None, callback=None):
        """ launch wrapper """    
        # accept only one thread
        if not name in self.threads or not self.threads[name].isAlive():
            self.threads[name] = ExecThread(command, cwd, callback)
            self.threads[name].start()
            if wait:
                self.threads[name].join()
        else:
            raise ExecManagerBusyError, "ExecManager is busy"

    def get_state(self, name):
        """ get thread execution state """
        return (self.threads[name].code, 
            xmlrpclib.Binary(self.threads[name].output))

    def get_status(self):
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
        if not status:
            status.append(_("Ready"))
        return status


class ExecThread(threading.Thread):
    """ Base class for running tasks """

    def __init__(self, command, cwd, callback):
        #threading.Thread.__init__(self, **kwds)
        self.process = None
        self.command = command
        self.cwd = cwd
        self.callback = callback
        self.code = 2000
        self.output = ""
        self.lock = threading.RLock()
        threading.Thread.__init__(self)

    def run(self):
        """ run command """
        self.process = Popen(self.command, stdout=PIPE, stderr=STDOUT,
            bufsize=1, shell=False, cwd=self.cwd)
        self.get_output()
        return 0

    def get_output(self):
        """ get command context """
        while self.isAlive():  
            # get the file descriptor of the process stdout pipe
            # for reading
            try:
                fd = select.select([self.process.stdout.fileno()],
                    [], [], 5)[0][0]
            # raise an exception when the process doesn't make output
            # for long time
            except IndexError:
                fd = None
                pass
              
            self.process.poll()
            if self.process.returncode == None:
                # get bytes one by one
                if fd:
                    self.lock.acquire()
                    self.output += os.read(fd, 1)
                    self.lock.release()
            else:
                # get last bytes from output
                if fd:
                    self.lock.acquire()
                    self.output += os.read(fd, 4096)
                    self.lock.release()
                self.code = self.process.returncode
                if self.callback:
                    self.callback(self.code, self.output)
                break


class ExecManagerError(Exception):
    """Base class for exceptions in ExecManager."""

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class ExecManagerBusyError(ExecManagerError):
    pass
