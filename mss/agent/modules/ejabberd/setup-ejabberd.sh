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

info_b $"The instant messaging service is configured."
info $"You can simply add users through the management interface at https://@HOSTNAME@/mmc/. The user's mail will be used as his Jabber ID."
info $"Use $HOST.$DOMAIN as the server."
info $"If $HOST.$DOMAIN is setup as a Jabber server in the $DOMAIN DNS zone there is no need to configure the server address in client."
