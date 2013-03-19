#!/bin/bash
# Copyright Mandriva 2009, 2010 all rights reserved

. '../functions.sh'

check_mmc_configured

fw_lan="$1"
fw_wan="$2"

base_reseau_template="templates/network.ini.tpl"
base_dhcpd_template="templates/dhcpd.conf.tpl"

# check if DNS module is enabled
dns_enable=1
[ ! -f /var/lib/named/etc/named.conf ] && dns_enable=0

###### now /etc/mmc/plugin/network.ini
backup /etc/mmc/plugins/network.ini
cat $base_reseau_template > /etc/mmc/plugins/network.ini
sed -i "s/\@SUFFIX\@/$MDSSUFFIX/" /etc/mmc/plugins/network.ini
sed -i "s/\@HOSTNAME\@/$HOST/" /etc/mmc/plugins/network.ini
sed -i "s/\@DNSENABLE\@/$dns_enable/" /etc/mmc/plugins/network.ini

###### now /etc/dhcpd.conf
backup /etc/dhcpd.conf
cat $base_dhcpd_template > /etc/dhcpd.conf
sed -i "s/\@SUFFIX\@/$MDSSUFFIX/" /etc/dhcpd.conf
sed -i "s/\@PASSWORD\@/$MDSPASS_E/" /etc/dhcpd.conf
sed -i "s/\@HOSTNAME\@/$HOST/" /etc/dhcpd.conf
chmod 640 /etc/dhcpd.conf

restart_service mmc-agent /var/log/mmc/mmc-agent.log
enable_service dhcpd

# configure the Firewall
[ $fw_lan == "on" ] && mss-add-shorewall-rule -a ACCEPT -t lan -p udp -P 67:68
[ $fw_wan == "on" ] && mss-add-shorewall-rule -a ACCEPT -t wan -p udp -P 67:68
restart_service shorewall

info_b $"The DHCP service is installed."
info $"You can now configure your DHCP settings from the management interface : https://@HOSTNAME@/mmc/"

exit 0
