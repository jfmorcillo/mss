import urllib2
import json

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from django.conf import settings
from django.template import RequestContext

from mss.lib.xmlrpc import XmlRpc

xmlrpc = XmlRpc()


@csrf_exempt
def user_error_submit(request):
    if request.method == "POST" and "error" in request.POST:
        result = xmlrpc.call('get_option', 'machine-id')
        data = {
            'machine': result,
            'error': request.POST['error'],
            'traceback': request.POST['simple_traceback'],
            'user_notes': request.POST['user_notes']
        }
        try:
            req = urllib2.Request(settings.TRACEBACK_API_URL)
            req.add_header('Content-Type', 'application/json')
            urllib2.urlopen(req, json.dumps(data))
        except:
            pass

        return render_to_response('errors/traceback_sent.html', {},
                                  context_instance=RequestContext(request))
