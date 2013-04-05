# -*- coding: UTF-8 -*-
#
# (c) 2010-2013 Mandriva, http://www.mandriva.com/
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

import json
import threading
import logging
import urllib2
import urllib
import time

from mss.agent.managers.translation import TranslationManager

_ = TranslationManager().translate
logger = logging.getLogger(__name__)


class RequestThread(threading.Thread):
    """ Base class for running HTTP requests """

    def __init__(self, type, module, url, params, headers, callback):
        self._code = 2000
        self._progress = 0
        self._result = None
        # thread type (config, install...)
        self.type = type
        self.module = module
        self.url = url
        self.params = params
        self.headers = headers
        self.callback = callback
        threading.Thread.__init__(self)

    def __repr__(self):
        return "<%s(%s, %s)>" % (self.__class__.__name__, self.module, self.url)

    @property
    def output(self):
        return " %s" % str(self._progress)

    @property
    def code(self):
        return self._code

    def run(self):
        """ run command """
        if self.params:
            self.params = urllib.urlencode(self.params)
        request = urllib2.Request(self.url, self.params)
        for header in self.headers:
            request.add_header(header[0], header[1])
        request.add_header('Accept-Language', TranslationManager().get_lang().split('_')[0] + ',en')
        response = urllib2.urlopen(request)
        start = time.time()
        logger.debug("Start: %s" % str(start))
        self.chunk_read(response, report_hook=self.chunk_report)
        end = time.time()
        logger.debug("End: %s" % str(end))
        logger.debug("Last: %ss" % str(end - start))

    def chunk_read(self, response, chunk_size=512, report_hook=None):
        total_size = response.info().getheader('Content-Length').strip()
        total_size = int(total_size)
        bytes_so_far = 0

        while 1:
            chunk = response.read(chunk_size)
            bytes_so_far += len(chunk)

            if not chunk:
                break
            elif not self._result:
                self._result = chunk
            else:
                self._result += chunk

            if report_hook:
                report_hook(bytes_so_far, chunk_size, total_size)

        # Request finished
        self._code = response.getcode()
        if response.info().gettype() == "application/json":
            result = json.loads(self._result)
        else:
            result = self._result

        if self.callback:
            self.callback(self.module, self._code, result)
        logger.debug("Finished request %s" % self.type)

    def chunk_report(self, bytes_so_far, chunk_size, total_size):
        percent = float(bytes_so_far) / total_size
        percent = round(percent*100, 2)
        self._progress = percent
        logger.debug("Downloading: %s%%" % self._progress)

    def stop(self):
        """ stop current process if exists"""
        try:
            self.process.terminate()
            self.join()
        except OSError:
            pass
        except AttributeError:
            pass
