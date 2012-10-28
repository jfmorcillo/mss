#!/bin/bash
# Copyright Mandriva 2012 all rights reserved

# $1 hostname
# $2 domain
# $3 encryption

. '../functions.sh'

check_mmc_configured

SERVICE="ejabberd"
EJABBERD_CONF_TEMPLATE="templates/ejabberd.cfg.tpl"
EJABBERD_CONF="/etc/ejabberd/ejabberd.cfg"

hostname=$1
domain=$2

##### ejabberd.cfg generation
backup $EJABBERD_CONF
cat $EJABBERD_CONF_TEMPLATE > $EJABBERD_CONF
sed -i "s/\@DOMAIN\@/$domain/" $EJABBERD_CONF
sed -i "s/\@SUFFIX\@/$MDSSUFFIX/" $EJABBERD_CONF

restart_service $SERVICE

echo "8The instant messaging service is configured."
echo "8You can simply add users through the management interface at# https://@HOSTNAME@/mmc/. #The user's mail will be used as his Jabber ID."
echo "7Configure clients with JID like# @B@uid@$domain@B@ #and use# @B@$hostname.$domain@B@ #as the server."
echo "7If# @B@$hostname.$domain@B@ #is registered as a Jabber server in the DNS zone# @B@$domain@B@ #there is no need to configure the server address in clients."
