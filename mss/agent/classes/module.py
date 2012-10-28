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
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime
from IPy import IP

from mss.agent.classes.media import Media
from mss.agent.classes.validation import Validation
from mss.agent.managers.translation import TranslationManager

_ = TranslationManager().translate

class Module(object):
    """
    Base class for all modules instances

    """

    def __init__(self, path, MM, arch):
        self.MM = MM
        self.logger = logging.getLogger()
        self.path = path
        self.arch = arch
        try:
            tree = ET.parse(os.path.join(self.path, "desc.xml"))
        except:
            raise Exception("Syntax error in desc.xml (%s)" % self.path)
        self.root = tree.getroot()
        # BDD access
        self.conn = sqlite3.connect('/var/lib/mss/mss-agent.db')
        # load module info
        self.load()
        # get module config object
        self.module = None
        # get current module config
        f, p, d = imp.find_module(self.id)
        try:
            # load module
            self.module = imp.load_module(self.id, f, p, d)
        except Exception, err:
            self.logger.error("Can't load module %s __init__.py :" % self.id)
            self.logger.error("%s" % err)
        self.check_configured()

    def load(self):
        """ load module basic infos """
        # get common info
        self.id = self.root.attrib.get("id")
        TranslationManager().set_catalog(self.id, self.path)
        self._name = self.root.findtext("name")
        self._desc = self.root.findtext("desc")
        self._actions = []
        for action in self.root.findall("actions/action"):
            self._actions.append(action.attrib)
        self._market = False
        if self.root.findtext("market/buy_url"):
            self._market = {}
            self._market['buy_url'] = self.root.findtext("market/buy_url")
            self._market['info_url'] = self.root.findtext("market/info_url")
            self._market['info_file'] = self.root.findtext("market/info_file")
            self._market['info_title'] = self.root.find("market/info_file").attrib["title"]
        # get module deps
        self._deps = [m.text for m in self.root.findall("deps/module")]
        # get module conflicts
        self._conflicts = [m.text for m in self.root.findall("conflicts/module")]
        # get preinst text
        if self.root.findtext("preinst/text"):
            self._preinst = self.root.findtext("preinst/text")
        else:
            self._preinst = " "

    @property
    def name(self):
        return _(self._name, self.id)

    @property
    def desc(self):
        if self._desc:
            return _(self._desc, self.id)
        else:
            return ""

    @property
    def actions(self):
        return self._actions

    @property
    def market(self):
        return self._market

    @property
    def deps(self):
        return self._deps

    @property
    def conflicts(self):
        return self._conflicts

    @property
    def preinst(self):
        return _(self._preinst, self.id).strip()

    def check_configured(self):
        # check if module is configured by calling module method
        if self.module:
            method = getattr(self.module, "check_configured", None)
            if method:
                try:
                    self._configured = method()
                    return
                except:
                    pass
    	# check if module is configured from database
        c = self.conn.cursor()
        c.execute('select * from module where name=?', (self.id,))
        if c.fetchone():
            self._configured = True
        else:
            self._configured = False
        c.close()
        # if the module has no configuration consider it is configured
        try:
            script, args = getattr(self.module, 'get_config_info')()
        except AttributeError:
            script, args = (None, [])
        if script == None:
            self._configured = True

    @property
    def configured(self):
        return self._configured

    @configured.setter
    def configured(self, value):
        self._configured = value
        if value:
            c = self.conn.cursor()
            c.execute('select * from module where name=?', (self.id,))
            if c.fetchone():
                c.execute('update module set configured=? where name=?', (datetime.now(), self.id))
            else:
                c.execute('insert into module values (?,?)', (self.id, datetime.now()))
            self.conn.commit()
            c.close()

    @property
    def installed(self):
        return self._installed

    @installed.setter
    def installed(self, value):
        self._installed = value

    @property
    def packages(self):
        """ get packages for module """
        if not getattr(self, "_packages", None):
            # get packages for current arch
            self._packages = []
            targets = self.root.findall("packages/target")
            for target in targets:
                if target.attrib['name'] == "all" or \
                   target.attrib['name'] == self.arch:
                    self._packages += [rpm.text for rpm in target.findall("rpm")]
        return self._packages

    @property
    def medias(self):
        """ get medias for module """
        media = self.root.find("medias")
        if media is not None:
            name = self.id
            verbose_name = media.attrib.get("verbose_name", name)
            auth = media.attrib.get("auth", None)
            can_skip = media.attrib.get("can_skip", False)
            urls = []
            # format media URL with correct arch
            for url in media.findall("url"):
                urls.append(re.sub('@ARCH@', self.arch, url.text))
            proto = media.attrib.get("proto", "http")
            mode = media.attrib.get("mode", None)
            return Media(name, verbose_name, urls, auth, proto, mode, can_skip)
        else:
            return None

    def get_config(self):
        """ get module current config """
        reload(self.module)
        # get current module config
        try:
            current_config = getattr(self.module, 'get_current_config')(self)
        except AttributeError:
            current_config = {}
        except Exception, err:
            self.logger.error("Error in get_current_config in %s module : " % self.id)
            self.logger.error(str(err))
            self.logger.error("Can't get module current config")
            current_config = {}
        # get script name and args order
        try:
            script, args = getattr(self.module, 'get_config_info')()
        except AttributeError:
            script, args = (None, [])

        # reset config
        self.config = []

        # no config script we skip the configuration
        if not script:
            self.config.append({'id': self.id, 'skip_config': True, 'do_config': False})
        # we have a config script
        else:
            self.config.append({'id': self.id, 'skip_config': False, 'do_config': False})
            # get XML config
            fields = self.root.findall("config/*")
            if fields:
                # if we have fields, show the configuration page
                self.config[0]['do_config'] = True
                self.config[0]['configured'] = self.configured
            for field in fields:
                field_config = field.attrib
                field_help = field.findtext("help")
                field_label = field.findtext("label")
                field_config["id"] = self.id
                field_config["help"] = _(field_help, self.id)
                field_config["label"] = _(field_label, self.id)
                field_config["type"] = field.tag
                if field_config["type"] == "options":
                    options = field.findall("option")
                    field_config["options"] = []
                    for option in options:
                        field_config["options"].append(
                            {'name': option.text,
                             'value': option.attrib.get('value')}
                        )
                if field_config["type"] == "custom":
                    self.config = getattr(self.module, 'get_%s_config' % field_config['name'])(self.config)
                # add current value if module is configured
                if self.configured and current_config.get(field_config['name']):
                    field_config['default'] = current_config.get(field_config['name'])
                # calculate default value if not configured
                if not self.configured and "default" in field_config:
                    # check if the default value is a module's method
                    try:
                        if isinstance(field_config["default"], basestring):
                            field_config["default"] = getattr(self.module, field_config["default"])(self)
                    except AttributeError:
                        # not a method
                        # get default value for multi fields
                        if "multi" in field_config and "default" in field_config:
                            if isinstance(field_config["default"], basestring):
                                default = field_config["default"].split(";")
                                field_config["default"] = default
                    except Exception, err:
                        self.logger.error("Error in %s() in %s module : " % (field_config["default"], self.id))
                        self.logger.error(str(err))
                        self.logger.error("Can't calculate default field value")
                        field_config["default"] = ""

                # reset require attribute if field is hidden for reconfiguration
                if self.configured and "show_if_unconfigured" in field_config and "require" in field_config:
                    del field_config["require"]

                if field_config["type"] != "custom":
                    self.config.append(field_config)

        return self.config

    def valid_config(self, user_config):

        """ valid user configuration for module """
        if not getattr(self, "config", None):
            self.config = self.get_config()

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
                        ip = re.match("^"+self.id+"_"+field_name+"_([0-9]?)_ip$", user_field)
                        if ip:
                            net = ip.group(1)
                            ip = user_config.get(self.id+"_"+field_name+"_"+net+"_ip")
                            mask = user_config.get(self.id+"_"+field_name+"_"+net+"_mask")
                            field_value.append((ip, mask))
                # handle multi text fields
                elif "multi" in field:
                    field_value = []
                    for user_field, user_value in user_config.items():
                        f = re.match("^"+self.id+"_"+field_name+"_([0-9]?)_field$", user_field)
                        if f:
                            nb = f.group(1)
                            value = user_config.get(self.id+"_"+field_name+"_"+nb+"_field")
                            field_value.append(value)
                # handle checkboxes
                elif field_type == "check":
                    # if box uncheck, set default to off otherwise value is None
                    field_value = user_config.get(self.id+"_"+field_name, "off")
                # set values for text,password,options fields
                else:
                    field_value = user_config.get(self.id+"_"+field_name)

                # set default value
                field["default"] = field_value

                # check if field is not empty
                if field.get("require"):
                    if not field_value:
                        errors = True
                        field["error"] = _("This field can't be empty.", "agent")
                    elif field_name.endswith("passwd"):
                        field_value2 = user_config.get(self.id+"_"+field_name+"2")
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
                        method = getattr(self.module, field.get("validation"), None)
                        module = self.id
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
                    self.MM.set_option(field["name"], field["default"])

        # store config if no errors
        if not errors:
            self.config = validated_config

        return (errors, validated_config)

    def info_config(self):
        # get script name and args order
        try:
            script, args = getattr(self.module, 'get_config_info')()
        except AttributeError:
            script, args = (None, [])
        # get args values
        args_values = []

        for arg in args:
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

        return (self.path, script, args_values)

    def __str__(self):
        return "%s : %s" % (self.name, self.desc)
