#!/bin/bash
# Copyright Mandriva 2012 all rights reserved

. '../functions.sh'

check_mmc_configured

SERVICE="httpd"
SERVICE_MMC="mmc-agent"
PG_CONF_FILE="/var/lib/pgsql/data/pg_hba.conf"
DAVICAL_CONF_TEMPLATE="templates/config.php.tpl"
DAVICAL_MMC_HOOK="templates/davical.py"
DAVICAL_CONF="/etc/davical/config.php"
APACHE_DAVICAL_CONF_TEMPLATE="templates/davical.conf.tpl"
APACHE_DAVICAL_CONF="/etc/httpd/conf/webapps.d/davical.conf"
DAVICAL_CRON_TEMPLATE="templates/davical.cron.tpl"
DAVICAL_CRON="/etc/cron.d/davical"
roundcube_db_conf_template="templates/config.inc.php.tpl"
DAVICAL_MMC_CONF="/etc/mmc/plugins/davical.ini"

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

backup $DAVICAL_MMC_CONF
sed -i "s/^user = .*/user = admin/" $DAVICAL_MMC_CONF
sed -i "s/^pswd =.*/pswd = $DAVICAL_ADMIN_PASS/" $DAVICAL_MMC_CONF

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


backup /usr/share/roundcubemail/plugins/calendar/config.inc.php
cat $roundcube_db_conf_template > /usr/share/roundcubemail/plugins/calendar/config.inc.php
sed -i "s/\@MDSSERVER\@/$MDSSERVER/" /usr/share/roundcubemail/plugins/calendar/config.inc.php
sed -i "s/^\$rcmail_config\['plugins'\].*/\$rcmail_config['plugins'] = array('managesieve', 'subscriptions_option', 'calendar');/" /etc/roundcubemail/main.inc.php

sqlite /var/lib/roundcubemail/sqlite.db < /usr/share/roundcubemail/plugins/calendar/SQL/sqlite.sql

# http -> https redirection
https_redirect davical $APACHE_DAVICAL_CONF

# install MMC hook
mkdir -p /etc/mmc/hooks/
cp ${DAVICAL_MMC_HOOK} /etc/mmc/hooks/

###Open the firewall port
#No need to open a particular port as Davical listen on the standard http port that should be already opened

echo "Stopping PostGre"
service postgresql stop
sed -i "s,#unix_socket_directory = '',unix_socket_directory= '/var/run/postgresql/',g" /var/lib/pgsql/data/postgresql.conf
echo "Starting PostGre"
chown -R postgres:postgres /var/run/postgresql
service postgresql start

###Sync the ldap user list with Davical user list (user provisioning)
#first time sync
su apache -c "/usr/bin/php --define 'error_reporting = E_ALL & ~E_DEPRECATED & ~E_NOTICE' /usr/share/davical/scripts/cron-sync-ldap.php $FQDN"
#cron rule for later sync
cat $DAVICAL_CRON_TEMPLATE > $DAVICAL_CRON
sed -i "s/\@FQDN\@/$FQDN/" $DAVICAL_CRON

restart_service $SERVICE
restart_service $SERVICE_MMC

info_b $"The calendar and addressbook service is configured."

info $"- each user can access its personnal calendar at https://@HOSTNAME@/davical/caldav.php/[user_email]/calendar/ using a calendar client (Thunderbird with Lightning, iCal...)"
info $"- you can add shared calendars at https://@HOSTNAME@/mmc/"

exit 0
