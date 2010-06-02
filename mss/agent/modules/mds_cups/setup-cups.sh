#!/bin/bash
# Copyright Mandriva 2009, 2010 all rights reserved
if [ "`id -u`" != "0" ]; then
	echo "Error, must be root user"
	exit 1
fi

. '../functions.sh'

/sbin/service cups restart 2>&1 > /dev/null
if [ $? -eq 0 ]; then echo "0Service Cups reloaded succesfully."
else echo "2Service Cups fails restarting. Check# /var/log/syslog"; sleep 1; exit 1
fi

chkconfig cups on

echo "8Cups is running."
echo "7You can add new printers from local Cups web interface : http://localhost:631/"

exit 0
