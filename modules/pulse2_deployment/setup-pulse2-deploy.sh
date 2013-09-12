#!/bin/bash
# Copyright Mandriva 2013 all rights reserved

# INCLUDES
. '../functions.sh'

check_mmc_configured

TMP_DIR=/var/lib/pulse2/package-server-tmpdir


# Tune PHP: increase maximum upload filesize
sed -i 's!^upload_max_filesize = .*$!upload_max_filesize = 150M!' /etc/php.ini
sed -i 's!^post_max_size = .*$!post_max_size = 150M!' /etc/php.ini
restart_service httpd

# Create package directory
mkdir -p $TMP_DIR
chmod 777 $TMP_DIR
chmod o+t $TMP_DIR
sed -i "/src = \/var\/lib\/pulse2\/packages/ {n; s/^tmp_input_dir.*/tmp_input_dir = \/var\/lib\/pulse2\/package-server-tmpdir/}" /etc/mmc/pulse2/package-server/package-server.ini

# Enable plugins
sed -i 's!^disable.*$!disable = 0!' /etc/mmc/plugins/msc.ini
sed -i 's!^disable.*$!disable = 0!' /etc/mmc/plugins/pkgs.ini
restart_service mmc-agent

enable_service pulse2-scheduler
enable_service pulse2-launchers
enable_service pulse2-package-server
service pulse2-scheduler stop
restart_service pulse2-scheduler
service pulse2-launchers stop
restart_service pulse2-launchers
service pulse2-package-server stop
restart_service pulse2-package-server

# Setup the firewall
cp -f macro.Pulse2Deployment /etc/shorewall
network=`grep Pulse2Inventory /etc/shorewall/rules | head -n1 | awk '{ print $2 }' | sed 's/[0-9]$//'`
mss-add-shorewall-rule -a Pulse2Deployment/ACCEPT -t $network
restart_service shorewall

# INFORMATION
info_b $"Pulse2 deployment module is installed and configured."
info $"The module is available on the management interface at https://@HOSTNAME@/mmc/."
info $"Check the documentation to use Pulse2 deployment features."

exit 0
