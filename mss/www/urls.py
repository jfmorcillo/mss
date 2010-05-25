from django.conf.urls.defaults import *
import settings

urlpatterns = patterns('django.views.generic.simple',
    (r'^$', 'redirect_to', { 'url': '/mss/'})
)

urlpatterns += patterns('',
    (r'^mss/', include('mss.urls')),
)

if settings.DEV:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
    urlpatterns += patterns('',
        (r'^404/', 'django.views.generic.simple.direct_to_template', {'template': '404.html'}),
        (r'^500/', 'django.views.generic.simple.direct_to_template', {'template': '500.html'}),
    )
