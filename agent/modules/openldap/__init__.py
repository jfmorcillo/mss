#!/usr/bin/python
# -*- coding: UTF-8 -*-

def get_config_info():
    return ("ldap.sh", ['dc', 'passwd'])

def get_current_config():
    return {'dc': 'toto.com', 'passwd': 'tutu'}
