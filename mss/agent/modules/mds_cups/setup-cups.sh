#!/bin/bash
# Copyright Mandriva 2009, 2010 all rights reserved
if [ "`id -u`" != "0" ]; then
	echo "Error, must be root user"
	exit 1
fi

. '../functions.sh'

restart_service cups
enable_service cups

echo "8The printing service is running."
echo "7You can add new printers from the Cups web interface : https://@HOSTNAME@:631/"

exit 0
