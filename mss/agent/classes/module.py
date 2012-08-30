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

class Module:
    """
    Base class for all modules instances

    """

    def __init__(self, path, TM, arch):
        self.TM = TM
        global _
        _ = self.TM.translate
        self.logger = logging.getLogger()
        self.path = path
        self.arch = arch
        tree = ET.parse(os.path.join(self.path, "desc.xml"))
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
        self.TM.set_catalog(self.id, self.path)
        self._name = self.root.findtext("name")
        self._desc = self.root.findtext("desc")
        self._infos = {}
        self._infos['url'] = self.root.findtext("info/url")
        self._infos['buy'] = self.root.findtext("info/buy")
        self._infos['file'] = self.root.findtext("info/file")
        # get module deps
        self._deps = [m.text for m in self.root.findall("deps/module")]
        # get module conflicts
        self._conflicts = [m.text for m in self.root.findall("conflicts/module")]
        # get preinst text
        if self.root.findtext("preinst/text"):
            self._preinst = self.root.findtext("preinst/text")
        else:
            self._preinst = " "


    def get_name(self):
        return _(self._name, self.id)
    name = property(get_name)

    def get_desc(self):
        return _(self._desc, self.id)
    desc = property(get_desc)

    def get_infos(self):
        return self._infos
    infos = property(get_infos)

    def get_deps(self):
        return self._deps
    deps = property(get_deps)

    def get_conflicts(self):
        return self._conflicts
    conflicts = property(get_conflicts)

    def get_preinst(self):
        return _(self._preinst, self.id).strip()
    preinst = property(get_preinst)

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

    def get_configured(self):
        return self._configured

    def set_configured(self, value):
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

    def get_installed(self):
        return self._installed

    def set_installed(self, value):
        self._installed = value

    def get_packages(self):
        """ get packages for module """
        if not getattr(self, "packages", None):
            # get packages for current arch
            self.packages = []
            targets = self.root.findall("packages/target")
            for target in targets:
                if target.attrib['name'] == "all" or \
                   target.attrib['name'] == self.arch:
                    self.packages += [rpm.text for rpm in target.findall("rpm")]
        return self.packages

    def get_medias(self):
        """ get medias for module """
        media = self.root.find("medias")
        if media:
            name = self.id
            verbose_name = media.attrib.get("verbose_name", name)
            auth = media.attrib.get("auth", None)
            urls = []
            # format media URL with correct arch
            for url in media.findall("url"):
                urls.append(re.sub('@ARCH@', self.arch, url.text))
            proto = media.attrib.get("proto", "http")
            mode = media.attrib.get("mode", None)
            return Media(name, verbose_name, urls, auth, proto, mode)
        else:
            return None

    def get_config(self):
        """ get module current config """
        reload(self.module)
        # get current module config
        try:
            current_config = getattr(self.module, 'get_current_config')()
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
                self.config[0]['configured'] = self.get_configured()
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
                # get default value for multi fields
                if "multi" in field_config and "default" in field_config:
                    if type(field_config["default"]) == str:
                        default = field_config["default"].split(";")
                        field_config["default"] = default
                # add current value if module is configured
                if self.get_configured() and current_config.get(field_config['name']):
                    field_config['default'] = current_config.get(field_config['name'])
                # calculate default value if not configured
                if not self.get_configured() and "default" in field_config:
                    # check if the default value is a module's method
                    try:
                        field_config["default"] = getattr(self.module, field_config["default"])()
                    except AttributeError:
                        # not a method
                        pass
                    except Exception, err:
                        self.logger.error("Error in %s() in %s module : " % (field_config["default"], self.id))
                        self.logger.error(str(err))
                        self.logger.error("Can't calculate default field value")
                        field_config["default"] = ""
                # reset require attribute if field is hidden for reconfiguration
                if self.get_configured() and "show_if_unconfigured" in field_config and "require" in field_config:
                    del field_config["require"]

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
