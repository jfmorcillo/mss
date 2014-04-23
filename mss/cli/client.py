# -*- coding: utf-8 -*-
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

from  mss.lib.xmlrpc import XmlRpc
import logging
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
h = logging.StreamHandler()
h.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(h)


def log_off():
    logger.setLevel(logging.CRITICAL)


class ConfigurationError(Exception):
    pass


class ConnectionError(Exception):
    pass


class Client:
    """ This class manages connections to a MSS agent. """
    def __init__(self, host="127.0.0.1", port="8001"):
        self.xmlrpc = XmlRpc(host=host, port=port)

    def debug(self):
        logger.setLevel(logging.DEBUG)

    def wait_for_task(self, task_type, module="agent"):
        """ Pool every second if 'type' thread is finished.
        Task_type are 'load_module','install','config', ...?"""
        while True:
            a = self.xmlrpc.call('get_state', task_type, module)
            code, output = a
            if code == 2000:
                pass
            else:
                break
            time.sleep(1)

    def call(self, method, *args):
        return self.xmlrpc.call(method, *args)

    def authenticate(self, login, passwd):
        logger.info('[Authentication] User: %s' % login)
        return self.xmlrpc.call("authenticate", login, passwd)

    def get_available_modules():
        pass

    def load_module(self, module_name):
        logger.info('Loading module %s...' % module_name)
        self.xmlrpc.call('load_modules', module_name)

    def install_module(self, module_name, sync=False):
        """ Load and Install module"""
        # self.load_module(module_name)

        logger.info('Installing module packages...')
        self.xmlrpc.call('install_modules', [module_name])
        if sync:
            self.wait_for_task('install')
            logger.info('Installing module package... done')

    def configure_module(self, module_name, config):
        """ Install module if needed. This method is synchone."""
        self.install_module(module_name, sync=True)

        # logger.info('Get configuration...')
        # module_config = self.xmlrpc.call('get_config', [module_name])
        logger.info('Configuring module...')
        config['continue'] = ''
        cfg = self.xmlrpc.call('valid_config', [module_name], config)
        logger.debug('Configuring module (run_config)...')
        self.xmlrpc.call('run_config', module_name)
        self.wait_for_task('config', module_name)
        logger.debug('Configuring module (end_config)...')
        self.xmlrpc.call('end_config', module_name, 0, "")
        logger.info('Configuring module... done')

    def get_configuration(self, module_name):
        """ Return module configuration """
        self.load_module(module_name)
        return self.xmlrpc.call('get_config', [module_name])[0]

    def get_require_fields(self, module_name):
        acc = []
        for r in self.get_configuration(module_name):
            if 'name' in r:
                if 'require' in r and r['require'] == 'yes':
                    acc.append(r)
        return acc
