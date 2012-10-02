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
import select
import threading
from subprocess import Popen, PIPE, STDOUT

class ProcessThread(threading.Thread):
    """ Base class for running tasks """

    def __init__(self, command, cwd, callback, shell, env):
        self.process = None
        self.command = command
        self.cwd = cwd
        self.callback = callback
        self._code = 2000
        self._output = ""
        self.lock = threading.RLock()
        self.shell = shell
        self.env = env
        threading.Thread.__init__(self)

    @property
    def output(self):
        return self._output.decode("UTF-8")

    @property
    def code(self):
        return self._code

    def run(self):
        """ run command """
        self.process = Popen(self.command, stdout=PIPE, stderr=STDOUT,
            bufsize=1, cwd=self.cwd, shell=self.shell, env=self.env)
        self.catch_output()
        return 0

    def stop(self):
        """ stop current process if exists"""
        try:
            self.process.terminate()
            self.join()
        except OSError:
            pass

    def catch_output(self):
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
                    self._output += os.read(fd, 1)
                    self.lock.release()
            else:
                # get last bytes from output
                if fd:
                    self.lock.acquire()
                    while os.read(fd, 1):
                        self._output += os.read(fd, 4096)
                    self.lock.release()
                self._code = self.process.returncode
                if self.callback:
                    self.callback(self._code, self._output)
                break
