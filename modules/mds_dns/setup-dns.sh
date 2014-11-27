#!/bin/bash
# Copyright Mandriva 2009, 2010 all rights reserved

. '../functions.sh'

check_mmc_configured

stop_service named-sdb
stop_service named

mds_network_template="templates/network.ini.tpl"
bind_template="templates/named.conf.tpl"
bind_conf="/var/lib/named/etc/named.conf"

networks="$1"
forwarders="$2"
fw_lan="$3"
fw_wan="$4"

ln -sf /var/lib/named/var/named/ /var/named

# check if DHCP module is enabled
dhcp_enable=1
[ ! -f /etc/dhcpd.conf ] && dhcp_enable=0

backup /etc/mmc/plugins/network.ini
cat $mds_network_template > /etc/mmc/plugins/network.ini
sed -i "s/\@SUFFIX\@/$MDSSUFFIX/" /etc/mmc/plugins/network.ini
sed -i "s/\@HOSTNAME\@/$HOST/" /etc/mmc/plugins/network.ini
sed -i "s/\@DHCPENABLE\@/$dhcp_enable/" /etc/mmc/plugins/network.ini

# create acl file
acl_file="/var/lib/named/etc/mss_acls.conf"
echo 'acl "mss" {' > $acl_file
echo "127.0.0.1/32;" >> $acl_file
if [ -z "$networks" ]; then
    warning $"No networks are authorized to make external queries."
else
    for network in $networks
    do
        echo "$network;" >> $acl_file
    done
fi
echo "};" >> $acl_file

# create forward file
forward_file="/var/lib/named/etc/mss_forwarders.conf"
touch $forward_file
if [ ! -z "$forwarders" ]; then
    # fill forwarders file
    echo "forwarders {" > $forward_file
    for forwarder in $forwarders
    do
        echo "$forwarder;" >> $forward_file
    done
    echo "};" >> $forward_file
else
    # empty forwarders file
    echo "" > $forward_file
fi

backup $bind_conf
cp $bind_template $bind_conf

touch /var/named/named.conf.ldap

restart_service named-sdb
enable_service named-sdb
restart_service mmc-agent /var/log/mmc/mmc-agent.log

# configure the Firewall
[ $fw_lan == "on" ] && mss-add-shorewall-rule -a DNS/ACCEPT -t lan
[ $fw_wan == "on" ] && mss-add-shorewall-rule -a DNS/ACCEPT -t wan
restart_service shorewall

info_b $"The DNS service is running."
if [ ! -z "$forwarders" ]; then
    info $"Your DNS will forward external queries to : $forwarders"
fi
if [ ! -z "$networks" ]; then
    info $"The following networks are able to query your DNS for external domains : $networks"
fi
info $"You can now add DNS zones in the management interface : https://@HOSTNAME@/mmc/"

exit 0
