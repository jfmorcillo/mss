import logging
import Cookie
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

from mss.agent.managers.module import ModuleManager

logger = logging.getLogger(__name__)
UNAUTHENTICATED_METHODS = ('set_lang', 'get_lang',
                           'get_status', 'get_state', 'get_option',
                           'check_net', 'update_medias')


class MSSXMLRPCRequestHandler(SimpleXMLRPCRequestHandler):

    def setCookie(self, key=None, value=None):
        if key:
            c1 = Cookie.SimpleCookie()
            c1[key] = value
            cinfo = self.getDefaultCinfo()
            for attr,val in cinfo.items():
                c1[key][attr] = val

            if c1 not in self.cookies:
                self.cookies.append(c1)

    def getDefaultCinfo(self):
        cinfo = {}
        cinfo['expires'] = 30*24*60*60
        cinfo['path'] = '/RPC2/'
        cinfo['comment'] = 'MSS-AGENT'
        cinfo['domain'] = self.request.getsockname()[0]
        cinfo['max-age'] = 30*24*60*60
        cinfo['secure'] = ''
        cinfo['version'] = 1
        return cinfo

    def do_POST(self):
        """Handles the HTTP POST request.

        Attempts to interpret all HTTP POST requests as XML-RPC calls,
        which are forwarded to the server's _dispatch method for handling.
        """
        # Note: this method is the same as in SimpleXMLRPCRequestHandler,
        # just hacked to handle cookies

        # Check that the path is legal
        if not self.is_rpc_path_valid():
            self.report_404()
            return

        try:
            # Get arguments by reading body of request.
            # We read this in chunks to avoid straining
            # socket.read(); around the 10 or 15Mb mark, some platforms
            # begin to have problems (bug #792570).
            max_chunk_size = 10*1024*1024
            size_remaining = int(self.headers["content-length"])
            L = []
            while size_remaining:
                chunk_size = min(size_remaining, max_chunk_size)
                L.append(self.rfile.read(chunk_size))
                size_remaining -= len(L[-1])
            data = ''.join(L)

            # In previous versions of SimpleXMLRPCServer, _dispatch
            # could be overridden in this class, instead of in
            # SimpleXMLRPCDispatcher. To maintain backwards compatibility,
            # check to see if a subclass implements _dispatch and dispatch
            # using that method if present.
            response = self.server._marshaled_dispatch(
                    data, getattr(self, '_dispatch', None)
                )
        except: # This should only happen if the module is buggy
            # internal error, report as HTTP server error
            self.send_response(500)
            self.end_headers()
        else:
            # got a valid XML RPC response
            self.send_response(200)
            self.send_header("Content-type", "text/xml")
            self.send_header("Content-length", str(len(response)))

            # HACK :start -> sends cookies here
            if self.cookies:
                for cookie in self.cookies:
                    self.send_header('Set-Cookie', cookie.output(header=''))
            # HACK :end

            self.end_headers()
            self.wfile.write(response)

            # shut down the connection
            self.wfile.flush()
            self.connection.shutdown(1)

    def _dispatch(self, method, params):
        self.cookies = []

        if method == 'authenticate':
            return self.authenticate(*params)
        elif method in UNAUTHENTICATED_METHODS or self.check_token():
            try:
                return ModuleManager()._dispatch(method, params)
            except Exception:
                logger.exception("Error while calling ModuleManager.%s" % method)
                raise
        else:
            raise Exception(u"Authentication failed")

    def authenticate(self, login, password):
        token = ModuleManager().authenticate(login, password)
        if token:
            # set authentication cookie
            self.setCookie('Token', token)
            return True
        return False

    def check_token(self):
        if self.headers.has_key('Token'):
            # handle cookie based authentication
            token = self.headers.get('Token')
            return ModuleManager().check_token(token)
        return False
