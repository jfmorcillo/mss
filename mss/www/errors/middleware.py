import sys
import traceback
import logging

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseServerError, Http404, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.encoding import smart_unicode
from django.core.urlresolvers import reverse
from django.contrib.auth import logout

from mss.lib.xmlrpc import XMLRPCError

logger = logging.getLogger(__name__)


class CatchExceptions(object):
    """Middleware shows tracebacks, and gets user feedback on what went wrong."""

    def process_exception(self, request, exception):
        if isinstance(exception, Http404):
            return Http404()

        if type(exception) != PermissionDenied:

            if type(exception) == XMLRPCError:
                context = {}
                context['xmlrpc_errno'] = exception.errno
                context['xmlrpc_error'] = exception.error

                if request.is_ajax():
                    return HttpResponseServerError(exception.error)
                else:
                    if 'Authentication failed' in exception.error:
                        logout(request)
                        return HttpResponseRedirect(reverse('login'))
                    else:
                        html = render_to_string("errors/error.html",
                                                context, context_instance=RequestContext(request))
                        return HttpResponseServerError(html, content_type='text/html')
            else:
                context = {}
                exc_info = sys.exc_info()
                try:
                    exception_value = smart_unicode(exc_info[1])
                    if exception_value != u"":
                        context['exception_value'] = exception_value
                except:
                    pass

                try:
                    context['simple_traceback'] = "\\n".join(
                        traceback.format_exception(*exc_info))
                except:
                    context['simple_traceback'] = ""

                html = render_to_string("errors/500.html",
                                        context, context_instance=RequestContext(request))
                return HttpResponseServerError(html, content_type='text/html')

        return None
