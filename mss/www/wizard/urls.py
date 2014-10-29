# -*- coding: UTF-8 -*-
#
# (c) 2010-2012 Mandriva, http://www.mandriva.com/
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

from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

urlpatterns = patterns('mss.www.wizard.views',
    url(r'^$', RedirectView.as_view(url='account/login/')),
    url(r'^setlang/$', 'set_language', name="set_language"),
    url(r'^has_net/(?P<has_net>[\d]+)/$', 'has_net', name="has_net"),
    url(r'^account/login/$', 'mylogin', name="login"),
    url(r'^account/logout/$', 'mylogout', name="logout"),
    url(r'^sections/$', 'sections', name="sections"),
    url(r'^sections/(?P<section>[\w]+)/$', 'section', name="section"),
    url(r'^status/$', 'get_status', name="status"),
    url(r'^state/(?P<thread>[\w]+)/$', 'get_state', {'module': 'agent'}, name="state"),
    url(r'^state/(?P<thread>[\w]+)/(?P<module>[\w-]+)/$', 'get_state'),
    url(r'^reload/$', 'reload_packages', name="reload_packages"),
    url(r'^prepare/$', 'prepare', name="prepare"),
    url(r'^preinst/$', 'preinst', name="preinst"),
    url(r'^download/$', 'download', name="download"),
    url(r'^download/module/(?P<module>[\w_-]+)/$', 'download_module', name="download_module"),
    url(r'^medias/auth/$', 'medias_auth', name="medias_auth"),
    url(r'^medias/add/$', 'medias_add', name="medias_add"),
    url(r'^medias/update/$', 'medias_update', name="medias_update"),
    url(r'^media/add/(?P<module>[\w_-]+)/(?P<repository>[\w-]+)/$', 'add_media', name="add_media"),
    url(r'^install/$', 'install', name="install"),
    url(r'^config/$', 'config', name="config"),
    url(r'^config/validation/$', 'config_valid', name="config_valid"),
    url(r'^config/run/(?P<module>[\w_-]+)/$', 'config_run', name="config_run"),
    url(r'^config/end/(?P<module>[\w_-]+)/$', 'config_end', name="config_end"),
    url(r'^reboot/run/$', 'reboot_run', name="reboot_run"),
    url(r'^end/$', 'end', name="end"),
)
