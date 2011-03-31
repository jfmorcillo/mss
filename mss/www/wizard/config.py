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

import glob
import imp
import os

class ConfigManager:

    class __ConfigManager:

        layout = []

        def load(self):
            configs = glob.glob(os.path.join(os.path.dirname(__file__),
                "..", "layout", "*", "config.py"))
            for config in sorted(configs):
                name = config.split("/")[-1].rstrip('.py')
                module = imp.load_source(name, config)

        def get_sections(self):
            return self.layout

        def get_section(self, section):
            for sec in self.layout:
                if sec["id"] == section:
                    return sec

        def get_section_modules(self, section):
            section = self.get_section(section)
            modules = []
            for bundle in section["bundles"]:
                for module in bundle["modules"]:
                    modules.append(module)
            return modules

        def add_section(self,  section):
            if not section in self.layout:
                section["bundles"] = []
                self.layout.append(section)

        def add_bundle(self, section, bundle):
            for sec in self.layout:
                if sec["id"] == section:
                    if not bundle in sec["bundles"]:
                        sec["bundles"].append(bundle)
                        break

        def add_module(self, section, bundle, module):
            for sec in self.layout:
                if sec["id"] == section:
                    for bdl in sec["bundles"]:
                        if bdl["id"] == bundle:
                            if not module in bdl["modules"]:
                                bdl["modules"].append(module)

    instance = None

    def __init__(self):
        if not ConfigManager.instance:
            ConfigManager.instance = ConfigManager.__ConfigManager()
            ConfigManager.instance.load()

    def __getattr__(self, attr):
        return getattr(self.instance, attr)

    def __setattr__(self, attr, val):
        return setattr(self.instance, attr, val)
