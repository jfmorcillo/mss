from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import sys

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--threads', action='store', dest='threads', default=10),
        make_option('--ssl-certificate', action='store', dest='ssl_certificate', default=None),
        make_option('--ssl-private-key', action='store', dest='ssl_private_key', default=None),
    )
    help = "Starts the MSS web server."
    args = '[optional port number, or ipaddr:port]'

    requires_model_validation = False

    def handle(self, addrport='', *args, **options):
        from django.conf import settings
        from django.core.handlers.wsgi import WSGIHandler
        from cherrypy.wsgiserver import CherryPyWSGIServer, WSGIPathInfoDispatcher
        from cpserver.mediahandler import MediaHandler
        from cpserver.translogger import TransLogger

        if args:
            raise CommandError('Usage is runmss %s' % self.args)
        if not addrport:
            addr = '0.0.0.0'
            port = '8000'
        else:
            try:
                addr, port = addrport.split(':')
            except ValueError:
                addr, port = '', addrport

        if not addr:
            addr = '0.0.0.0'

        if not port.isdigit():
            raise CommandError('%r is not a valid port number' % port)

        threads = options.get('threads', 10)
        ssl_certificate = options.get('ssl_certificate', None)
        ssl_private_key = options.get('ssl_private_key', None)
        quit_command = (sys.platform == 'win32') and 'CTRL-BREAK' or 'CONTROL-C'
        use_reloader = settings.DEBUG
        show_log = settings.DEBUG

        def inner_run():
            if ssl_private_key and ssl_certificate:
                print "MSS server is running at https://%s:%s/" % (addr, port)
            else:
                print "MSS server is running at http://%s:%s/" % (addr, port)
            if settings.DEBUG:
                print "Devel mode is ON"
                print "Quit the server with %s." % quit_command

            app = WSGIHandler()
            path = {}
            if show_log:
                logged_app = TransLogger(app)
                path['/'] = logged_app
            else:
                path['/'] = app
            path[settings.MEDIA_URL] = MediaHandler(settings.MEDIA_ROOT)
            dispatcher = WSGIPathInfoDispatcher(path)
            server = CherryPyWSGIServer((addr, int(port)), dispatcher, threads)

            if ssl_private_key and ssl_certificate:
                from cherrypy.wsgiserver.ssl_pyopenssl import pyOpenSSLAdapter
                server.ssl_adapter = pyOpenSSLAdapter(ssl_certificate, ssl_private_key, None)

            try:
                server.start()
            except KeyboardInterrupt:
                server.stop()
                sys.exit(0)

        if use_reloader:
            from django.utils import autoreload
            autoreload.main(inner_run)
        else:
            inner_run()
