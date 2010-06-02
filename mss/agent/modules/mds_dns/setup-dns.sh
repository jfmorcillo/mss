#!/bin/bash
# Copyright Mandriva 2009, 2010 all rights reserved
if [ "`id -u`" != "0" ]; then
	echo "Error, must be root user"
	exit 1
fi

. '../functions.sh'

mds_network_template="templates/network.ini.tpl"
bind_template="templates/named.conf.tpl"
bind_conf="/var/lib/named/etc/named.conf"

mds_base_ini="/etc/mmc/plugins/base.ini"

mdssuffix=`grep '^baseDN' $mds_base_ini | sed 's/^.*[[:space:]]\+=[[:space:]]\+//'`

networks="$1"
forwarders="$2"

ln -sf /var/lib/named/var/named/ /var/named

backup /etc/mmc/plugins/network.ini
cat $mds_network_template > /etc/mmc/plugins/network.ini
sed -i "s/\@SUFFIX\@/$mdssuffix/" /etc/mmc/plugins/network.ini
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

/sbin/service mmc-agent restart > /dev/null 2>&1
if [ $? -eq 0 ]; then echo "0Service MMC reloaded succesfully."
else echo "2Service MMC fails restarting. Check /var/log/mmc/mmc-agent.log"; sleep 1; exit 1
fi

/sbin/service named restart > /dev/null 2>&1
if [ $? -eq 0 ]; then echo "0Service named reloaded succesfully."
else echo "2Service named fails restarting. Check /var/log/syslog"; sleep 1; exit 1
fi

chkconfig named on

echo "8DNS module is activated in the MDS interface."
if [ ! -z "$forwarders" ]; then
    echo "7Your DNS will forward external queries to : #$forwarders"
fi
if [ ! -z "$networks" ]; then
    echo "7The following networks are able to query your DNS for external domains : #$networks"
fi
echo "7You can now add DNS zones from the MDS interface : http://@HOSTNAME@/mmc/"
echo "8Make sure you have enabled the DNS service (port 53) on your firewall."

exit 0
