from django.core.management.base import BaseCommand
from optparse import make_option
import sys

class Command( BaseCommand ):

    option_list = BaseCommand.option_list + (
        make_option('--noreload', action='store_false', dest='use_reloader', default=True),
    )
    help = "Starts the CherryPy WSGI server for development."
    args = '[optional port number, or ipaddr:port]'

    requires_model_validation = False

    def handle(self, addrport='', *args, **options):
        import django
        from django.core.handlers.wsgi import WSGIHandler
        from cpserver.wsgiserver import CherryPyWSGIServer, WSGIPathInfoDispatcher
        from cpserver.mediahandler import MediaHandler
        from cpserver.translogger import TransLogger

        if args:
            raise CommandError('Usage is runcpserver %s' % self.args)
        if not addrport:
            addr = ''
            port = '8000'
        else:
            try:
                addr, port = addrport.split(':')
            except ValueError:
                addr, port = '', addrport
        if not addr:
            addr = '127.0.0.1'

        if not port.isdigit():
            raise CommandError('%r is not a valid port number' % port)

        use_reloader = options.get('use_reloader', True)
        quit_command = (sys.platform == 'win32') and 'CTRL-BREAK' or 'CONTROL-C'

        def inner_run():
            from django.conf import settings
            print 'Validating models...'
            self.validate(display_num_errors=True)
            print "\nDjango version %s, using settings %r" % (django.get_version(), settings.SETTINGS_MODULE)
            print "CherryPy development server is running at http://%s:%s/" % (addr, port)
            print "Quit the server with %s." % quit_command

            app = WSGIHandler()
            logged_app = TransLogger(app)
            path = { '/': logged_app,
                    settings.MEDIA_URL: MediaHandler(settings.MEDIA_ROOT),
                    #settings.ADMIN_MEDIA_PREFIX:
                    #    MediaHandler(
                    #        os.path.join(django.contrib.admin.__path__[0],'media')
                    #    )
                   }
            dispatcher = WSGIPathInfoDispatcher(path)
            server = CherryPyWSGIServer((addr, int(port)),dispatcher)

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
