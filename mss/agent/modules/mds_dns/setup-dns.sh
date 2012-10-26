#!/bin/bash
# Copyright Mandriva 2009, 2010 all rights reserved

. '../functions.sh'

check_mmc_configured

mds_network_template="templates/network.ini.tpl"
bind_template="templates/named.conf.tpl"
bind_conf="/var/lib/named/etc/named.conf"

networks="$1"
forwarders="$2"

ln -sf /var/lib/named/var/named/ /var/named

backup /etc/mmc/plugins/network.ini
cat $mds_network_template > /etc/mmc/plugins/network.ini
sed -i "s/\@SUFFIX\@/$MDSSUFFIX/" /etc/mmc/plugins/network.ini
if [ $? -eq 0 ]; then echo "0MDS configuration done. (/etc/mmc/plugins/network.ini updated)";
else echo "2Error while configuring MDS. (/etc/mmc/plugins/network.ini)"; sleep 1; exit 1
fi

# create acl file
acl_file="/var/lib/named/etc/mss_acls.conf"
echo 'acl "mss" {' > $acl_file
echo "127.0.0.1/32;" >> $acl_file
if [ -z "$networks" ]; then
    echo "1No networks are authorized to make external queries."
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

restart_service mmc-agent /var/log/mmc/mmc-agent.log
restart_service named
enable_service named

echo "8The DNS service is running."
if [ ! -z "$forwarders" ]; then
    echo "7Your DNS will forward external queries to : #$forwarders"
fi
if [ ! -z "$networks" ]; then
    echo "7The following networks are able to query your DNS for external domains : #$networks"
fi
echo "7You can now add DNS zones in the management interface : http://@HOSTNAME@/mmc/"
echo "8Make sure you have enabled the DNS service (port 53) on your firewall."

exit 0
