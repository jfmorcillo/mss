#!/bin/bash
# Copyright Mandriva 2012 all rights reserved

. '../functions.sh'

check_mmc_configured

SERVICE="httpd"
PG_CONF_FILE="/var/lib/pgsql/data/pg_hba.conf"
DAVICAL_CONF_TEMPLATE="templates/config.php.tpl"
DAVICAL_CONF="/etc/davical/config.php"
APACHE_DAVICAL_CONF_TEMPLATE="templates/davical.conf.tpl"
APACHE_DAVICAL_CONF="/etc/httpd/conf/webapps.d/davical.conf"
DAVICAL_CRON_TEMPLATE="templates/davical.cron.tpl"
DAVICAL_CRON="/etc/cron.d/davical"

###Give Davical access to the Postgre DB
backup $PG_CONF_FILE
#remove any previous Davical configuration
sed -i "s/^.*davical.*$//" $PG_CONF_FILE
#http://www.davical.org/installation.php recommends to add these lines at the top of pg configuration file
sed -i -e '/# TYPE  DATABASE        USER            ADDRESS                 METHOD/ a\
local   davical    davical_app   trust\
local   davical    davical_dba   trust' $PG_CONF_FILE

restart_service postgresql

# Wait postgres to be up
# TODO replace with somthing smarter
for (( i=10 ; i ; i-=1 )); do sleep 1; echo -n '.'; done

# Drop any Davical DB
su postgres -c 'dropdb davical' 2>/dev/null
# Create the DB
su postgres -c /usr/share/davical/dba/create-database.sh 2>&1
# Get the generated password from the DB
DAVICAL_ADMIN_PASS=`su postgres -c "psql davical -c 'select username, password from usr;'" | sed -n '/admin/s/^ *admin.*\*\*\(.*\)$/\1/p'`

[ ! $DAVICAL_ADMIN_PASS ] && error $"Failed to setup the database." && exit 1

###Enable acces to Davical folder
backup $APACHE_DAVICAL_CONF
cat $APACHE_DAVICAL_CONF_TEMPLATE > $APACHE_DAVICAL_CONF
#TODO check that this conf is not too much permissive
#TODO switch to a vhost

###Now the true configuration
backup $DAVICAL_CONF
cat $DAVICAL_CONF_TEMPLATE > $DAVICAL_CONF
sed -i "s/\@MDSSERVER\@/$MDSSERVER/" $DAVICAL_CONF
sed -i "s/\@DOMAIN\@/$DOMAIN/" $DAVICAL_CONF
sed -i "s/\@SUFFIX\@/$MDSSUFFIX/" $DAVICAL_CONF
sed -i "s/\@FQDN\@/$FQDN/" $DAVICAL_CONF

# http -> https redirection
https_redirect davical $APACHE_DAVICAL_CONF

restart_service $SERVICE

###Open the firewall port
#No need to open a particular port as Davical listen on the standard http port that should be already opened

###Sync the ldap user list with Davical user list (user provisioning)
#first time sync
su apache -c "/usr/bin/php --define 'error_reporting = E_ALL & ~E_DEPRECATED & ~E_NOTICE' /usr/share/davical/scripts/cron-sync-ldap.php $FQDN"
#cron rule for later sync
cat $DAVICAL_CRON_TEMPLATE > $DAVICAL_CRON
sed -i "s/\@FQDN\@/$FQDN/" $DAVICAL_CRON

info_b $"The calendar and addressbook service is configured."
info $"- Administrator : admin"
info $"- Password : $DAVICAL_ADMIN_PASS"
info $"Change it using the management interface https://@HOSTNAME@/davical/"

info $"Use https://$HOST.$DOMAIN/davical/caldav.php/[user_email]/calendar/ to add calendar into caldav clients"
exit 0
