#!/bin/bash
# Copyright Mandriva 2012 all rights reserved

# $1 servername
# $2 encryption

if [ "`id -u`" != "0" ]; then
	echo "Error, must be root user"
	exit 1
fi

. '../functions.sh'
SERVICE="ejabberd"
EJABBERD_CONF_TEMPLATE="templates/ejabberd.cfg.tpl"
EJABBERD_CONF="/etc/ejabberd/ejabberd.cfg"
MDS_BASE_INI="/etc/mmc/plugins/base.ini"
MDSSERVER=127.0.0.1
CERTFILE="/etc/pki/tls/private/ejabberd.pem"

check_mmc_configured $MDS_BASE_INI

##### ejabberd.cfg generation
backup $EJABBERD_CONF
cat $EJABBERD_CONF_TEMPLATE > $EJABBERD_CONF
sed -i "s/\@SERVERNAME\@/$1/" $EJABBERD_CONF

case "$2" in
	starttls|tls)
	sed -i "s%\@ENCRYPTION\@%\{certfile, \"$CERTFILE\"\}, $2,%" $EJABBERD_CONF
	;;
	none)
		sed -i "s/\@ENCRYPTION\@/%% no encryption defined/" $EJABBERD_CONF
	;;
esac

sed -i "s/\@SUFFIX\@/$MDSSUFFIX/" $EJABBERD_CONF
sed -i "s/\@SERVER\@/$MDSSERVER/" $EJABBERD_CONF

restart_service $SERVICE

echo "8The instan messaging service is configured."
echo "8You can simply add users through the management interface at http://@HOSTNAME@/mmc/."
echo "8Configure clients with id: user_name@$1"
echo "8If $1 is registered into the DNS there no need to set the server IP address when configuring the client else it has to be configured"
##Post-installation
