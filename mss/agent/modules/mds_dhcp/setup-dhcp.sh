#!/bin/bash
# Copyright Mandriva 2009, 2010 all rights reserved

. '../functions.sh'

check_mmc_configured

fw_lan="$1"
fw_wan="$2"

base_reseau_template="templates/network.ini.tpl"
base_dhcpd_template="templates/dhcpd.conf.tpl"

ln -sf /var/lib/named/var/named/ /var/named

###### now /etc/mmc/plugin/network.ini
backup /etc/mmc/plugins/network.ini
cat $base_reseau_template > /etc/mmc/plugins/network.ini
sed -i "s/\@SUFFIX\@/$MDSSUFFIX/" /etc/mmc/plugins/network.ini
sed -i "s/\@HOSTNAME\@/$HOST/" /etc/mmc/plugins/network.ini
if [ $? -eq 0 ]; then echo "0Configuration done. (/etc/mmc/plugins/network.ini updated)";
else echo "2Error while configuring the dhcp service. (/etc/mmc/plugins/network.ini)"; exit 1
fi

###### now /etc/dhcpd.conf
backup /etc/dhcpd.conf
cat $base_dhcpd_template > /etc/dhcpd.conf
sed -i "s/\@SUFFIX\@/$MDSSUFFIX/" /etc/dhcpd.conf
sed -i "s/\@PASSWORD\@/$MDSPASS_E/" /etc/dhcpd.conf
sed -i "s/\@HOSTNAME\@/$HOST/" /etc/dhcpd.conf
chmod 640 /etc/dhcpd.conf
if [ $? -eq 0 ]; then echo "0Configuration of dhcp-server done. (/etc/dhcpd.conf updated)"
else echo "2Error while configuring the dhcp-server. (/etc/dhcpd.conf)"; exit 1
fi

restart_service mmc-agent /var/log/mmc/mmc-agent.log
enable_service dhcpd

# configure the Firewall
[ $fw_lan == "on" ] && mss-add-shorewall-rule -a ACCEPT -t lan -p udp -P 67:68
[ $fw_wan == "on" ] && mss-add-shorewall-rule -a ACCEPT -t wan -p udp -P 67:68
restart_service shorewall

echo 8The DHCP service is installed.
echo 7You can now configure your DHCP settings from the management interface : https://@HOSTNAME@/mmc/

exit 0
