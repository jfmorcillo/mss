import xmlrpclib
from socket import error as socket_error
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


class XmlRpc:
    """ Class to handle the xmlrpc calls """
    
    def __init__(self):
        self.conn = xmlrpclib.ServerProxy('http://localhost:8001')

    def call(self, method, *args):
        method = getattr(self.conn, method)
        try:
            return [False, method(*args)]
        except socket_error, err:
            return [HttpResponseRedirect(reverse('error', args=[err[0]])), False]
            
#         xmlrpclib.Fault, xmlrpclib.ProtocolError, xmlrpclib.ResponseError)
