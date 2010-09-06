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

    def __init__(self):
        self.SECTIONS = []
        self.SECTIONS_MODULES = {}
        self.load_configs()

    def load_configs(self):
        for config in glob.glob(os.path.join(os.path.dirname(__file__), 
            "..", "layout", "*", "config.py")):
            name = config.split("/")[-1].rstrip('.py')
            print name
            module = imp.load_source(name, config)
            if hasattr(module, "config"):
                self.SECTIONS += module.config.SECTIONS
                self.SECTIONS_MODULES.update(module.config.SECTIONS_MODULES)
            del module

    def get_sections(self):
        return self.SECTIONS
        
    def get_section(self, section):
        return self.SECTIONS_MODULES[section]

    def get_section_name(self, section):
        for sec in self.SECTIONS:
            if sec['id'] == section:
                return sec['name']
        return "?"
        
    def get_section_modules(self, section):
        section = self.get_section(section)
        modules = []
        for bundle in section:
            for module in bundle['modules']:
                modules.append(module)
        return modules

class Config:

    def __init__(self):
        self.SECTIONS = []
        self.SECTIONS_MODULES = {}

    def add_section(self,  section):
        self.SECTIONS.append(section)

    def add_modules(self, section, modules):
        self.SECTIONS_MODULES[section] = modules
