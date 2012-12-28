import sys
import traceback

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseServerError, Http404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.encoding import smart_unicode

class CatchExceptions(object):
    """Middleware shows tracebacks, and gets user feedback on what went wrong."""

    def process_exception(self, request, exception):
        if isinstance(exception, Http404):
            return Http404()

        if type(exception) != PermissionDenied:
            exc_info = sys.exc_info()

            context = {}
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
            return HttpResponseServerError(html, mimetype='text/html')


        return None
