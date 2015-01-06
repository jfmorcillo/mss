#!/bin/bash
# Copyright Mandriva 2013 all rights reserved

# INCLUDES
. '../functions.sh'

function get_pulse2_interfaces() {
  grep -q 'lan\|wan' /etc/shorewall/interfaces
  if [ $? -eq 0 ]; then
    echo `grep Pulse2Inventory /etc/shorewall/rules | awk '{ print $2 }' | sed -e 's/lan/eth/' -e 's/wan/eth/'`
  fi
}

function get_interface_addr() {
  iface=$1
  echo `ip addr show $iface | grep -o "inet [0-9]*\.[0-9]*\.[0-9]*\.[0-9]*" | sed 's/inet //'`
}

# CHECKS
check_mmc_configured

# PARAMETERS
# TODO: Remove and use the password from mysql directly'
myrootpasswd="$1"
fw_lan="$2"
fw_wan="$3"

ENABLE_FUSIONFILE=templates/020_enable_fusioninventory.sh
GLPI_CONFIG=templates/config_db.php

# Retrieve info from filesystem
LDAP_ADMINDN="uid=LDAP Admin,ou=System Accounts,$MDSSUFFIX"

# Setup the firewall
cp -f macro.Pulse2Inventory /etc/shorewall
[ $fw_lan == "on" ] && mss-add-shorewall-rule -a Pulse2Inventory/ACCEPT -t lan
[ $fw_wan == "on" ] && mss-add-shorewall-rule -a Pulse2Inventory/ACCEPT -t wan

# SSH key management
if [ ! -f /root/.ssh/id_rsa ]; then
	ssh-keygen -t rsa -b 2048 -f /root/.ssh/id_rsa -N '' > /dev/null 2>&1
    [ $? -ne 0 ] && error "Failed to generate a SSH key pair for Pulse2 services" && exit 1
fi
sed -i 's!^.*sshkey_default = .*$!sshkey_default = /root/.ssh/id_rsa!' /etc/mmc/pulse2/launchers/launchers.ini
sed -i "s|/root/.ssh/id_rsa'|/root/.ssh/id_rsa'|" /usr/sbin/pulse2-setup

# Configure inventory module to use GLPI
sed -i 's|# glpi_computer_uri = http://localhost/glpi/front/computer.form.php?id=|glpi_computer_uri = http://localhost/glpi/front/computer.form.php?id=|' /etc/mmc/plugins/glpi.ini
sed -i "s|# glpi_mode = False|glpi_mode = True|" /etc/mmc/pulse2/package-server/package-server.ini
sed -i "s|disable = 1|disable = 0|" /etc/mmc/plugins/glpi.ini

#overwritten by pulse2-setup
#sed -i "s|# enable_forward = False|enable_forward = True|" /etc/mmc/pulse2/inventory-server/inventory-server.ini
#sed -i "s|# url_to_forward = http://localhost/glpi/plugins/fusioninventory/front/plugin_fusioninventory.communication.php|url_to_forward = http://localhost/glpi/plugins/fusioninventory/front/plugin_fusioninventory.communication.php|" /etc/mmc/pulse2/inventory-server/inventory-server.ini

sed -i "s|#purge_machine = 0|purge_machine = 1|" /etc/mmc/plugins/glpi.ini
sed -i "s|#glpi_username = username|glpi_username = glpi|" /etc/mmc/plugins/glpi.ini
sed -i "s|#glpi_password = password|glpi_password = glpi|" /etc/mmc/plugins/glpi.ini
sed -i "s|method = inventory|method = glpi|" /etc/mmc/plugins/base.ini


# We fill the glpi database.
dbname="glpi"
dbuser="glpi"
dbpass=`randpass 10 1`

mysql_get_root_password $myrootpasswd

mysql_do_query "DROP USER ${dbuser}@'localhost';"
mysql_do_query "DROP DATABASE IF EXISTS ${dbname};"
mysql_do_query "CREATE DATABASE ${dbname};"
mysql_do_query "GRANT ALL ON ${dbname}.* to '${dbuser}'@'localhost' identified by '${dbpass}';"
mysql_do_query "FLUSH PRIVILEGES;"

mysql -u $dbuser -p$dbpass $dbname < /usr/share/glpi/install/mysql/glpi-0.84.1-empty.sql

# For security reason we delete the install folder
rm -frv /usr/share/glpi/install

cp  $GLPI_CONFIG /usr/share/glpi/config
sed -i "s/\@DBUSER\@/$dbuser/" /usr/share/glpi/config/config_db.php
sed -i "s/\@DBPASS\@/$dbpass/" /usr/share/glpi/config/config_db.php
sed -i "s/\@DBNAME\@/$dbname/" /usr/share/glpi/config/config_db.php

#Create initial entitie ( if not done pulse2 backtrace )
mysql_do_query "INSERT INTO glpi.glpi_entities (id ,name ,entities_id ,completename ,comment ,level ,sons_cache ,ancestors_cache) VALUES ( NULL , 'glpi', '0', 'glpi', '', '1', NULL , NULL )"

# Enable Fusion inventory plugins
php /usr/share/glpi/plugins/fusioninventory/scripts/cli_install.php &> /dev/null

# Enable fusioninventory
sh $ENABLE_FUSIONFILE

# Check DNS
dig ${FQDN} +nosearch +short | tail -n1 | grep -q -E '([0-9]{1,3}\.){3}[0-9]{1,3}'
is_dns_working=$?
# No DNS try to guess the IP address
if [ ! ${is_dns_working} -eq 0 ]; then
    # Get the first IP address we found
    ifaces=`get_pulse2_interfaces`
    nb_ifaces=`echo $ifaces | wc -w`

    if [ $nb_ifaces -eq 1 ]; then
        FQDN=`get_interface_addr $ifaces`
    elif [ $nb_ifaces -eq 0 ]; then
        error $"You need to allow access to the Pulse2 Inventory server on either internal or external networks."
        exit 1
    elif [ $nb_ifaces -gt 1 ]; then
        error $"A DNS entry must be set for this server if you want the Pulse2 services to listen on multiple interfaces."
        exit 1
    fi
fi
sed -i "s!^public_ip.*!public_ip = ${FQDN}!" /etc/mmc/pulse2/package-server/package-server.ini

# Generate pulse2 agents
cp /root/.ssh/id_rsa.pub /tmp/id_rsa.pub
sed -i 's!/root/.ssh/id_rsa.pub!/tmp/id_rsa.pub!g' /var/lib/pulse2/clients/win32/generate-agent-pack.sh
/var/lib/pulse2/clients/win32/generate-agent-pack.sh | grep -v '^7zsd.sfx' | grep -v '^7-Zip'
rm -f /tmp/id_rsa.pub

# Setup
mkdir -p /var/lib/pulse2/imaging/bootmenus
mkdir -p /var/lib/pulse2/imaging/computers

mysql_password=`cat /root/.my.cnf | grep password  | head -n1 | sed "s/password='\(.*\)'/\1/"`
pulse2-setup -b -R --reset-db \
 --mysql-host=localhost --mysql-user=root --mysql-passwd="$mysql_password" \
 --ldap-uri=ldap://$MDSSERVER/ --ldap-basedn="$MDSSUFFIX" --ldap-admindn="$LDAP_ADMINDN" --ldap-passwd="$MDSPASS" \
 --disable-package --glpi-enable --glpi-dbhost=localhost --glpi-dbname="glpi" --glpi-dbuser=root \
 --glpi-dbpasswd="$mysql_password" \
 --glpi-url="localhost/glpi"\
 | sed -r 's/\x1b.*?[mGKHh]//g'

# Disable agent threading
sed -i 's!^multithreading.*$!multithreading = 0!' /etc/mmc/agent/config.ini

# Disable unneeded modules
sed -i 's!^disable.*$!disable = 1!' /etc/mmc/plugins/msc.ini
sed -i 's!^disable.*$!disable = 1!' /etc/mmc/plugins/pkgs.ini
sed -i 's!^disable.*$!disable = 1!' /etc/mmc/plugins/imaging.ini

# Fix external IPs
sed -i "s!^public_ip.*!public_ip = ${FQDN}!" /etc/mmc/pulse2/package-server/package-server.ini
sed -i "s!^tcp_sproxy_host.*!tcp_sproxy_host = ${FQDN}!" /etc/mmc/pulse2/launchers/launchers.ini

stop_service pulse2-scheduler
stop_service pulse2-launchers
stop_service pulse2-package-server
disable_service pulse2-scheduler
disable_service pulse2-launchers
disable_service pulse2-package-server

restart_service mmc-agent
restart_service shorewall

info_b $"Pulse2 Inventory is installed and configured."
info $"The inventory is available on the management interface at https://@HOSTNAME@/mmc/."
info $"Check the documentation to use the Pulse2 inventory at http://serviceplace.mandriva.com/addons/mbs/1.0/pulse2_inventory/."

exit 0
