#!/bin/bash
# Copyright Mandriva 2012 all rights reserved

. '../functions.sh'

check_mmc_configured

fw_lan=$1
fw_wan=$2

SERVICE="ejabberd"
EJABBERD_CONF_TEMPLATE="templates/ejabberd.cfg.tpl"
EJABBERD_CONF="/etc/ejabberd/ejabberd.cfg"

##### ejabberd.cfg generation
backup $EJABBERD_CONF
cat $EJABBERD_CONF_TEMPLATE > $EJABBERD_CONF
sed -i "s/\@DOMAIN\@/$DOMAIN/" $EJABBERD_CONF
sed -i "s/\@SUFFIX\@/$MDSSUFFIX/" $EJABBERD_CONF

restart_service $SERVICE

# configure the Firewall
[ $fw_lan == "on" ] && mss-add-shorewall-rule -a JabberPlain/ACCEPT -t lan
[ $fw_wan == "on" ] && mss-add-shorewall-rule -a JabberPlain/ACCEPT -t wan
restart_service shorewall

echo "8The instant messaging service is configured."
echo "8You can simply add users through the management interface at# https://@HOSTNAME@/mmc/. #The user's mail will be used as his Jabber ID."
echo "7Configure clients with JID like# uid@$DOMAIN #and use# $HOST.$DOMAIN #as the server."
echo "7If# $HOST.$DOMAIN #is setup as a Jabber server in the DNS zone# $DOMAIN #there is no need to configure the server address in clients."
