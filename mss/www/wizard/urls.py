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

from django.conf.urls.defaults import *

urlpatterns = patterns('mss.www.wizard.views',
    url(r'^$', 'first_time', name="first_time"),
    url(r'^lang/(?P<lang>[\w_]+)/$', 'set_lang', name="set_lang"),
    url(r'^account/authentication/$', 'login_form', name="login_form"),
    url(r'^account/login/$', 'mylogin', name="login"),
    url(r'^account/logout/$', 'mylogout', name="logout"),
    url(r'^sections/$', 'sections', name="sections"),
    url(r'^sections/(?P<section>[\w]+)/$', 'section', name="section"),
    url(r'^error/(?P<code>[\d]+)/$', 'error', name="error"),
    url(r'^status/$', 'get_status', name="status"),
    url(r'^state/(?P<thread>[\w]+)/$', 'get_state', {'module': 'agent'}, name="state"),
    url(r'^state/(?P<thread>[\w]+)/(?P<module>[\w-]+)/$', 'get_state'),
    url(r'^reload/$', 'reload_packages', name="reload_packages"),
    url(r'^preinst/$', 'preinst', name="preinst"),
    url(r'^medias/$', 'medias', {'module': None}, name="medias"),
    url(r'^medias/add/$', 'medias_add', name="medias_add"),
    url(r'^medias/(?P<module>[\w-]+)/$', 'medias', name="medias_module"),
    url(r'^media/add/(?P<module>[\w-]+)/$', 'add_media', name="add_media"),
    url(r'^medias/update/$', 'medias_update', name="medias_update"),
    url(r'^install/$', 'install', name="install"),
    url(r'^config/$', 'config', name="config"),
    url(r'^config/validation/$', 'config_valid', name="config_valid"),
    url(r'^config/start/$', 'config_start', name="config_start"),
    url(r'^config/run/(?P<module>[\w-]+)/$', 'config_run', name="config_run"),
    url(r'^config/end/(?P<module>[\w-]+)/$', 'config_end', name="config_end"),
)
