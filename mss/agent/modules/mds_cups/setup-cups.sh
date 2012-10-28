#!/bin/bash
# Copyright Mandriva 2009, 2010 all rights reserved

. '../functions.sh'

check_mmc_configured

fw_lan="$1"
fw_wan="$2"

restart_service cups
enable_service cups

# configure the Firewall
[ $fw_lan == "on" ] && mss-add-shorewall-rule -a ACCEPT -t lan -p tcp -P 631
[ $fw_wan == "on" ] && mss-add-shorewall-rule -a ACCEPT -t wan -p tcp -P 631
restart_service shorewall

echo "8The printing service is running."
echo "7You can add new printers from the Cups web interface : https://@HOSTNAME@:631/admin/"
echo "7Login to the Cups interface is the root account."

exit 0
