#!/bin/bash
#
# MSS - Mandriva Server Setup Web
#
####################################
#
# Configuration
#
HOST=0.0.0.0
PORT=8000
SSL=1
SSL_CRT=/etc/mss/ssl/localhost.crt
SSL_KEY=/etc/mss/ssl/localhost.key
BASEDIR=/usr/lib/python2.7/site-packages/mss/www/
DAEMON=manage.py
GROUP=`id -gn`
#
####################################

test -f ${BASEDIR}${DAEMON} || exit 0
test -f /usr/bin/python || exit 0

[ ! -f $SSL_CRT ] && echo "SSL certificate not found" && SSL=0
[ ! -f $SSL_KEY ] && echo "SSL private key not found" && SSL=0

if [ $SSL == 1 ]; then
    SSL_OPTIONS="ssl_certificate=$SSL_CRT ssl_private_key=$SSL_KEY"
else
    SSL_OPTIONS=""
fi

cd $BASEDIR
/usr/bin/python $DAEMON runcpserver host=$HOST port=$PORT $SSL_OPTIONS server_group=$GROUP \
    server_user=$USER
