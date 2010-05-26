###########################################################################
# Configuration
#
# Django settings

import sys

sys.path.append("/usr/lib/python2.5/site-packages/mss/www/")
sys.path.append("/usr/lib/python2.5/site-packages/mss/")
DJANGO_SETTINGS = 'www.settings'
DJANGO_SERVE_ADMIN = False # Serve admin files

# Server settings
IP_ADDRESS = '0.0.0.0'
PORT = 8080
SERVER_NAME = 'localhost'
SERVER_THREADS = 3
# Change it to True if you want it to run as daemon, if you use a
# daemon.sh file you should also change it to True
RUN_AS_DAEMON = True
DAEMON_RUN_DIR = '/' # The daemon will change directory to this one
                     # this is needed to prevent unmounting your
                     # disk.

# Log settings
LOGFILE = '/tmp/mss-www.log'
LOGLEVEL = 'INFO' # if DEBUG is True, overwritten to DEBUG
DEBUG = True

# It must match with the path given in your daemon.sh file if you are
# using a daemon.sh file to control the server. 
PIDFILE = '/var/run/mss-www.pid' 

# Launch as root to dynamically chown
SERVER_USER = 'nobody'
SERVER_GROUP = 'nogroup'

# Enable SSL, if enabled, the certificate and private key must 
# be provided.
SSL = False
SSL_CERTIFICATE = '/full/path/to/certificate'
SSL_PRIVATE_KEY = '/full/path/to/private_key'

#
###########################################################################
