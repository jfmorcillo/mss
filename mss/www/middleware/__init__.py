import traceback

from django.http import HttpResponse
from django.utils.html import escape

class CatchAjaxException(object):

    def process_exception(self, request, exception):
        if request.is_ajax():
            url = request.META['REQUEST_URI']
            error = """
            var message = new Element('p', {'class': 'error'});
            message.update("Error while calling %s");
            var log = new Element('div', {'class': 'log'});
            log.update("%s");
            $('popup').appendChild(message);
            $('popup').appendChild(log);
            $("popup").addClassName("poptb");
            $('popup').show();
            """ % (url, escape(traceback.format_exc()).replace('\n', '\\n'))

            return HttpResponse(error, mimetype="application/javascript")
