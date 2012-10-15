#!/bin/bash
# Copyright Mandriva 2009, 2010 all rights reserved

if [ "`id -u`" != "0" ]; then
	echo "Error, must be root user"
	exit 1
fi

. '../functions.sh'


base_reseau_template="templates/network.ini.tpl"
base_dhcpd_template="templates/dhcpd.conf.tpl"

mds_base_ini="/etc/mmc/plugins/base.ini"

if [ ! -f $mds_base_ini ]; then
    echo "2MMC interface is not installed."
    echo "2Can't continue."
    exit 1
fi

mdssuffix=`grep '^baseDN' $mds_base_ini | sed 's/^.*[[:space:]]\+=[[:space:]]\+//'`
mdspass=`grep '^password' $mds_base_ini | sed 's/^.*[[:space:]]\+=[[:space:]]\+//'`
mdsserver=127.0.0.1

hostname=`hostname`

ln -sf /var/lib/named/var/named/ /var/named

###### now /etc/mmc/plugin/network.ini
backup /etc/mmc/plugins/network.ini
cat $base_reseau_template > /etc/mmc/plugins/network.ini
sed -i "s/\@SUFFIX\@/$mdssuffix/" /etc/mmc/plugins/network.ini
if [ $? -eq 0 ]; then echo "0Configuration done. (/etc/mmc/plugins/network.ini updated)";
else echo "2Error while configuring the dhcp service. (/etc/mmc/plugins/network.ini)"; exit 1
fi

###### now /etc/dhcpd.conf
backup /etc/dhcpd.conf
cat $base_dhcpd_template > /etc/dhcpd.conf
sed -i "s/\@SUFFIX\@/$mdssuffix/" /etc/dhcpd.conf
sed -i "s/\@PASSWORD\@/$mdspass/" /etc/dhcpd.conf
sed -i "s/\@HOSTNAME\@/$hostname/" /etc/dhcpd.conf
chmod 640 /etc/dhcpd.conf
if [ $? -eq 0 ]; then echo "0Configuration of dhcp-server done. (/etc/dhcpd.conf updated)"
else echo "2Error while configuring the dhcp-server. (/etc/dhcpd.conf)"; exit 1
fi

restart_service mmc-agent /var/log/mmc/mmc-agent.log
enable_service dhcpd

echo 8The DHCP service is installed.
echo 7You can now configure your DHCP settings from the management interface : http://@HOSTNAME@/mmc/

exit 0
