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
fw_lan="$1"
fw_wan="$2"

# Retrieve info from filesystem
LDAP_ADMINDN="uid=LDAP Admin,ou=System Accounts,$MDSSUFFIX"

# Setup the firewall
cp -f macro.Pulse2Inventory /etc/shorewall
[ $fw_lan == "on" ] && mss-add-shorewall-rule -a Pulse2Inventory/ACCEPT -t lan
[ $fw_wan == "on" ] && mss-add-shorewall-rule -a Pulse2Inventory/ACCEPT -t wan

# SSH key management
if [ ! -f /root/.ssh/id_rsa_pulse ]; then
	ssh-keygen -t rsa -b 2048 -f /root/.ssh/id_rsa_pulse -N '' > /dev/null 2>&1
    [ $? -ne 0 ] && error "Failed to generate a SSH key pair for Pulse2 services" && exit 1
fi
sed -i 's!^.*sshkey_default = .*$!sshkey_default = /root/.ssh/id_rsa_pulse!' /etc/mmc/pulse2/launchers/launchers.ini
sed -i "s!/root/.ssh/id_rsa'!/root/.ssh/id_rsa_pulse'!" /usr/sbin/pulse2-setup

# Check DNS
dig ${FQDN} +nosearch +short | tail -n1 | grep -q -E '([0-9]{1,3}\.){3}[0-9]{1,3}'
is_dns_working=$?
# No DNS try to guess the IP address
if [ ! ${is_dns_working} -eq 0 ]; then
    # Get the first IP address we found
    ifaces=`get_pulse2_interfaces`
    nb_ifaces=`echo $ifaces | wc -w`

    if [ $nb_ifaces -eq 1 ]; then
        addr=`get_interface_addr $ifaces`
        sed -i "s!^public_ip.*!public_ip = $addr!" /etc/mmc/pulse2/package-server/package-server.ini
    elif [ $nb_ifaces -eq 0 ]; then
        error $"You need to allow access to the Pulse2 Inventory server on either internal or external networks."
        exit 1
    elif [ $nb_ifaces -gt 1 ]; then
        error $"A DNS entry must be set for this server if you want the Pulse2 services to listen on multiple interfaces."
        exit 1
    fi
else
    sed -i "s!^public_ip.*!public_ip = ${FQDN}!" /etc/mmc/pulse2/package-server/package-server.ini
fi

# Generate pulse2 agents
cp /root/.ssh/id_rsa_pulse.pub /tmp/id_rsa.pub
sed -i 's!/root/.ssh/id_rsa.pub!/tmp/id_rsa.pub!g' /var/lib/pulse2/clients/win32/generate-agent-pack.sh.in
sed -i 's!/root/.ssh/id_rsa.pub!/tmp/id_rsa.pub!g' /var/lib/pulse2/clients/win32/generate-agent-pack.sh
/var/lib/pulse2/clients/win32/generate-agent-pack.sh | grep -v '^7zsd.sfx' | grep -v '^7-Zip'
rm -f /tmp/id_rsa.pub

# Setup
mkdir -p /var/lib/pulse2/imaging/bootmenus
mkdir -p /var/lib/pulse2/imaging/computers

mysql_password=`cat /root/.my.cnf | grep password  | head -n1 | sed "s/password='\(.*\)'/\1/"`
pulse2-setup -b -R --reset-db \
 --mysql-host=localhost --mysql-user=root --mysql-passwd="$mysql_password" \
 --ldap-uri=ldaps://$MDSSERVER/ --ldap-basedn="$MDSSUFFIX" --ldap-admindn="$LDAP_ADMINDN" --ldap-passwd="$MDSPASS" \
 --disable-imaging --disable-package --disable-backup | sed -r 's/\x1b.*?[mGKHh]//g'

# Disable agent threading
sed -i 's!^multithreading.*$!multithreading = 0!' /etc/mmc/agent/config.ini

# Disable unneeded modules
sed -i 's!^disable.*$!disable = 1!' /etc/mmc/plugins/msc.ini
sed -i 's!^disable.*$!disable = 1!' /etc/mmc/plugins/pkgs.ini

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
info $"Check the documentation to use the Pulse2 inventory."

exit 0
