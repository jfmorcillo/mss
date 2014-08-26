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
import re
import imp
import copy
import logging
import hashlib
import json
import zipfile
from datetime import datetime
from IPy import IP

from mss.agent.config import Config
from mss.agent.lib.db import get_session, ModuleTable
from mss.agent.lib.utils import grep
from mss.agent.classes.media import Media
from mss.agent.classes.validation import Validation
from mss.agent.managers.translation import TranslationManager
from mss.agent.managers.process import ProcessManager
from mss.agent.managers.module import ModuleManager

_ = TranslationManager().translate
logger = logging.getLogger(__name__)


class Module(object):
    """
    Base class for all modules instances

    """

    def __init__(self, desc):
        self._desc = desc
        self._path = desc["module"]["path"]
        self._module = None
        if self.downloaded:
            self.load_desc()
            self.load_module()
            self.load_translations()
        self.check_configured()
        self.check_installed()

    @property
    def details(self):
        return {'slug': self.slug,
                'name': self.name,
                'description': self.description,
                'url': self._desc.get("url", False),
                'actions': self.actions,
                'downloaded': self.downloaded,
                'installed': self.installed,
                'has_repositories': bool(self.repositories),
                'has_restricted_repositories': self.has_restricted_repositories,
                'has_configuration': self.has_configuration,
                'has_configuration_script': self.has_configuration_script,
                'configured': self.configured,
                'conflicts': self.conflicts,
                'dependencies': self.dependencies,
                'standalone': self.standalone,
                'price': self.price,
                'purshased': self.purshased,
                'can_download': self._desc.get('can_download', True),
                'reboot': self.reboot,
                'module': self._desc.get("module", {})}

    @property
    def slug(self):
        return self._desc.get("slug")

    @property
    def name(self):
        return _(self._desc.get('name', self.slug), self.slug)

    @property
    def description(self):
        if self._desc.get('desc', False):
            logger.warning("deprecated: desc must be renamed in description (%s)" % self.slug)
            return _(self._desc['desc'], self.slug)
        elif self._desc.get('description', False):
            return _(self._desc['description'], self.slug)
        else:
            return ""

    @property
    def actions(self):
        actions = self._desc.get("actions", [])
        for action in actions:
            action["name"] = _(action["name"], self.slug)
        return actions

    @property
    def dependencies(self):
        if "dependencies" in self._desc:
            logger.warning("deprecated: dependencies list must be stored in the module key (%s)" % self.slug)
            return self._desc.get("dependencies", [])
        elif self._desc.get("module", False):
            return self._desc["module"].get("dependencies", [])
        else:
            return []

    @property
    def conflicts(self):
        if "conflicts" in self._desc:
            logger.warning("deprecated: conflicts list must be stored in the module key (%s)" % self.slug)
            return self._desc.get("conflicts", [])
        elif self._desc.get("module", False):
            return self._desc["module"].get("conflicts", [])
        else:
            return []

    @property
    def price(self):
        return self._desc.get("price", 0)

    @property
    def purshased(self):
        return self._desc.get("purshased", False)

    @property
    def standalone(self):
        return self._desc.get("standalone", True)

    @property
    def reboot(self):
        if "postinstall" in self._desc:
            logger.warning("deprecated: reboot must be stored in the module key (%s)" % self.slug)
            return self._desc["postinstall"].get("reboot", False)
        if self._desc.get("module", False):
            return self._desc["module"].get("reboot", False)
        return False

    @property
    def category(self):
        # return first category of the list
        categories = self._desc.get("categories", [])
        if categories:
            category = copy.deepcopy(categories[0])
            category["name"] = _(category["name"], self.slug)
            return category
        else:
            return {u"slug": u"other", u"name": _("Other", "agent")}

    @property
    def section(self):
        if self._desc.get("module", False):
            return self._desc["module"].get("section", "other")
        else:
            return "other"

    @property
    def has_configuration(self):
        return "config" in self._desc

    @property
    def has_configuration_script(self):
        if getattr(self, "_script", False):
            return True
        return False

    def check_configured(self):
        # check if module is configured by calling module method
        if self._module:
            method = getattr(self._module, "check_configured", None)
            if method:
                try:
                    self._configured = method()
                    return
                except:
                    pass
        # check if module is configured from database
        session = get_session(Config().db_file)
        module = session.query(ModuleTable).filter(ModuleTable.name == self.slug).first()
        if module and module.configured:
            self._configured = True
        else:
            self._configured = False

    @property
    def configured(self):
        return self._configured

    @configured.setter
    def configured(self, value):
        self._configured = value
        if value:
            module = ModuleTable(self.slug)
            module.configured = datetime.now()
            session = get_session(Config().db_file)
            session.merge(module)
            session.commit()

    def check_installed(self):
        """ check if module is installed """
        if not self.downloaded:
            self.installed = False
            return
        packages = set(self.packages)
        # check if packages are installed
        if len(packages) == len(packages.intersection(ModuleManager().packages)):
            self.installed = True
        else:
            self.installed = False

    @property
    def installed(self):
        return self._installed

    @installed.setter
    def installed(self, value):
        self._installed = value

    @property
    def downloaded(self):
        return os.path.exists(os.path.join(self._path, "__init__.py"))

    @property
    def packages(self):
        """ get packages for module """
        if getattr(self, "_packages", None) is None:
            # get packages for current arch
            self._packages = []
            targets = self._desc.get("packages", [])
            for target in targets:
                if (target['name'] == "all" or
                        target['name'] == ModuleManager().arch):
                    self._packages.extend(target.get("rpms", []))
        return self._packages

    @property
    def repositories(self):
        """ get module repositories """
        self._repositories = []
        repositories = self._desc.get("repositories", [])
        if repositories:
            # Don't return repositories already installed
            for repository in repositories:
                repository['url'] = repository['url'].replace('@ARCH@', ModuleManager().arch)
                if 'url' in repository and not grep(repository['url'].split('://')[1], '/etc/urpmi/urpmi.cfg'):
                    repository['module_slug'] = self.slug
                    self._repositories.append(Media(**repository))
        return self._repositories

    @property
    def has_restricted_repositories(self):
        for repository in self.repositories:
            if repository.restricted:
                return True
        return False

    def get_config(self):
        """ get module current config """
        assert self._module
        reload(self._module)

        # get current module config
        try:
            current_config = getattr(self._module, 'get_current_config')(self)
        except AttributeError:
            current_config = {}
        except Exception, err:
            logger.error("Error in get_current_config in %s module : " % self.slug)
            logger.error(str(err))
            logger.error("Can't get module current config")
            current_config = {}

        # reset config
        self.config = []
        if self.has_configuration:
            # get XML config
            fields = self._desc.get("config", [])
            for field_config in fields:
                field_config["slug"] = self.slug
                # translate label and help fields
                if "label" in field_config:
                    field_config["label"] = _(field_config["label"], self.slug)
                if "help" in field_config:
                    field_config["help"] = _(field_config["help"], self.slug)
                # get dynamic configuration via a python method
                if field_config["type"] == "custom":
                    self.config = getattr(self._module, 'get_%s_config' % field_config['name'])(self.config)
                # add current value if module is configured
                if self.configured and current_config.get(field_config['name']):
                    field_config['default'] = current_config.get(field_config['name'])
                # calculate default value if not configured
                if not self.configured and "default" in field_config:
                    # check if the default value is a module's method
                    try:
                        if isinstance(field_config["default"], basestring):
                            field_config["default"] = getattr(self._module, field_config["default"])(self)
                    except AttributeError:
                        # not a method
                        # get default value for multi fields
                        if "multi" in field_config and "default" in field_config:
                            if isinstance(field_config["default"], basestring):
                                default = field_config["default"].split(";")
                                field_config["default"] = default
                    except Exception, err:
                        logger.error("Error in %s() in %s module : " % (field_config["default"], self.slug))
                        logger.error(str(err))
                        logger.error("Can't calculate default field value")
                        field_config["default"] = ""

                # reset require attribute if field is hidden for reconfiguration
                if self.configured and "show_if_unconfigured" in field_config and "require" in field_config:
                    del field_config["require"]

                if field_config["type"] != "custom":
                    self.config.append(field_config)

        return {"slug": self.slug, "config": self.config}

    def valid_config(self, user_config):
        """ valid user configuration for module """
        if not getattr(self, "config", None):
            self.get_config()

        validated_config = copy.deepcopy(self.config)
        errors = False

        for field in validated_config:
            field_name = field.get("name")
            field_type = field.get("type")
            if field_name:
                # set value for networks fields
                if field_type == "network":
                    field_value = []
                    for user_field, user_value in user_config.items():
                        match = re.match("^"+self.slug+"_"+field_name+"_([0-9]?)_(ip|mask)$", user_field)
                        if match:
                            net = match.group(1)
                            ip = user_config.get(self.slug+"_"+field_name+"_"+net+"_ip", '')
                            mask = user_config.get(self.slug+"_"+field_name+"_"+net+"_mask", '')
                            field_value.append((ip, mask))
                # handle multi text fields
                elif "multi" in field:
                    field_value = []
                    for user_field, user_value in user_config.items():
                        f = re.match("^"+self.slug+"_"+field_name+"_([0-9]?)_field$", user_field)
                        if f:
                            nb = f.group(1)
                            value = user_config.get(self.slug+"_"+field_name+"_"+nb+"_field").strip()
                            if value:
                                field_value.append(value)
                # handle checkboxes
                elif field_type == "check":
                    # if box uncheck, set default to off otherwise value is None
                    field_value = user_config.get(self.slug+"_"+field_name, "off")
                # set values for text,password,options fields
                else:
                    field_value = user_config.get(self.slug+"_"+field_name)

                # set default value
                field["default"] = field_value

                # check if field is not empty
                if field.get("require"):
                    if not field_value:
                        errors = True
                        field["error"] = _("This field can't be empty.", "agent")
                    elif field_name.endswith("passwd") and field.get("confirm", "yes") != "no":
                        field_value2 = user_config.get(self.slug+"_"+field_name+"2")
                        if field_value != field_value2:
                            errors = True
                            field["error"] = _("Password mismatch.", "agent")
                    else:
                        if field.get("error"):
                            del field["error"]

                # validate field data
                if field.get("validation"):
                    # get global validation method
                    method = getattr(Validation(), field.get("validation"), None)
                    module = "agent"
                    if not method:
                        # get module validation method
                        method = getattr(self._module, field.get("validation"), None)
                        module = self.slug
                    # run the validation method
                    if method and field_value:
                        result = method(field_value)
                        if result:
                            errors = True
                            field["error"] = _(result, module)
                        elif field.get("error"):
                            del field["error"]

                # store the field value in the DB
                if not 'error' in field and 'store' in field:
                    ModuleManager().set_option(field["name"], field["default"])

        # store config if no errors
        if not errors:
            self.config = validated_config

        return {"slug": self.slug, "config": validated_config, "errors": errors}

    def info_config(self):
        # get args values
        args_values = []
        for arg in self._script_args:
            for field in self.config:
                if arg == field.get('name'):
                    # network field values
                    if field.get("type") == "network":
                        value = ''
                        for ip, mask in field['default']:
                            network = ip+"/"+mask
                            if field.get("format") == "long":
                                network = str(IP(network))
                            else:
                                network = str(IP(network, make_net=True))
                            value += network+" "
                        value = value[:-1]
                        args_values.append(value)
                    # multi text field
                    elif "multi" in field:
                        value = ''
                        for text in field.get('default'):
                            value += text+" "
                        value = value[:-1]
                        args_values.append(value)
                    # other fields
                    else:
                        args_values.append(field.get('default'))

        return (self._path, self._script, args_values)

    def download(self):
        """ Download module if not present on disk """
        if not self.downloaded:
            assert self._desc['module']['file']
            logger.info("Download module: %s" % self.slug)
            if ModuleManager()._token:
                headers = [('Authorization', 'Token ' + ModuleManager()._token)]
            url = self._desc['module']['file']
            ProcessManager().download_module(url, headers=headers, callback=self.end_download)

    def end_download(self, module, code, result):
        if code == 200:
            temp_path = os.path.join("/tmp", self.slug + ".zip")
            with open(temp_path, "wb") as f:
                f.write(result)
        else:
            logger.error("Error while downloading %s module" % self.slug)

        if code == 200:
            # Verify sha1
            logger.debug("Unzip module: %s" % temp_path)
            sha1 = hashlib.sha1()
            with open(temp_path, "rb") as f:
                sha1.update(f.read())
            logger.debug("Process sha1sum: %s" % sha1.hexdigest())
            if sha1.hexdigest() == self._desc['module']['file_sha1']:
                logger.debug("Zip file is valid: unzip...")
                os.mkdir(self._path)
                zip = zipfile.ZipFile(temp_path)
                zip.extractall(path=self._path)
                os.unlink(temp_path)
                self.load_desc()
                self.load_module()
                self.load_translations()
                self.check_configured()
                self.check_installed()
            else:
                logger.error("Zip file is invalid...")

    def load_desc(self):
        if self.downloaded:
            logger.debug("Loading downloaded %s desc.json" % self.slug)
            with open(os.path.join(self._path, "desc.json")) as f:
                # Update current desc.json with the downloaded desc.json
                # Don't use the local name and description
                local_desc = json.load(f)
                for key, value in local_desc.items():
                    if key not in ("name", "description", "desc"):
                        self._desc[key] = value

    def load_module(self):
        logger.debug("Loading %s python module" % self.slug)
        f, p, d = imp.find_module(self.slug)
        try:
            self._module = imp.load_module(self.slug, f, p, d)
        except Exception, err:
            logger.error("Can't load module %s __init__.py :" % self.slug)
            logger.error("%s" % err)
        else:
            # get script name and args order
            try:
                self._script, self._script_args = getattr(self._module, 'get_config_info')()
            except AttributeError:
                self._script, self._script_args = (False, [])

    def load_translations(self):
        TranslationManager().set_catalog(self.slug, self._path)

    def __str__(self):
        return "%s : %s" % (self.name, self.description)
