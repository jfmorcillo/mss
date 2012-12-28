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

from django.conf.urls.defaults import patterns, include
import settings

urlpatterns = patterns('django.views.generic.simple',
    (r'^$', 'redirect_to', { 'url': '/mss/'})
)

urlpatterns += patterns('',
    (r'^mss/', include('mss.www.wizard.urls')),
    (r'^errors/', include('mss.www.errors.urls')),
    (r'^404/', 'django.views.generic.simple.direct_to_template', {'template': 'errors/404.html'}),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

