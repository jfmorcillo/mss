import glob
import imp
import os

class ConfigManager:

    def __init__(self):
        self.SECTIONS = []
        self.SECTIONS_MODULES = {}
        self.load_configs()

    def load_configs(self):
        for config in glob.glob(os.path.join(os.path.dirname(__file__), "modules", "*.py")):
            name = config.split("/")[-1].rstrip('.py')
            module = imp.load_source(name, config)
            if hasattr(module, "config"):
                self.SECTIONS += module.config.SECTIONS
                self.SECTIONS_MODULES.update(module.config.SECTIONS_MODULES)
            del module

    def get_sections(self):
        return self.SECTIONS
        
    def get_section(self, section):
        return self.SECTIONS_MODULES[section]
        
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
