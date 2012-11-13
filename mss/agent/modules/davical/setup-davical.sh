#!/bin/bash
# Copyright Mandriva 2012 all rights reserved

# $1 host

. '../functions.sh'

check_mmc_configured

SERVICE="httpd"
HOSTNAME=$1
PG_CONF_FILE="/var/lib/pgsql/data/pg_hba.conf"
DAVICAL_CONF_TEMPLATE="templates/config.php.tpl"
DAVICAL_CONF="/etc/davical/config.php"
APACHE_DAVICAL_CONF_TEMPLATE="templates/davical.conf.tpl"
APACHE_DAVICAL_CONF="/etc/httpd/conf/webapps.d/davical.conf"

###Give Davical access to the Postgre DB
backup $PG_CONF_FILE
#remove any previous Davical configuration
sed -i "s/^.*davical.*$//" $PG_CONF_FILE
#http://www.davical.org/installation.php recommends to add these lines at the top of pg configuration file
 sed -i -e '/# TYPE  DATABASE        USER            ADDRESS                 METHOD/ a\
local   davical    davical_app   trust\
local   davical    davical_dba   trust' $PG_CONF_FILE

restart_service postgresql

#sometimes posgres takes too much time to restart and breaks
#TODO replace with somthing smarter
for (( i=20 ; i ; i-=1 )); do sleep 1; echo -n '.'; done

###Create Davical DB
#TODO: check that DB don't already exists
su postgres -c /usr/share/davical/dba/create-database.sh 2>&1
#when this script ends it prints the admin password it should be printed to the user of MSS
#get the generated password from the DB
DAVICAL_ADMIN_PASS=`su postgres -c "psql davical -c 'select username, password from usr;'" | sed -n '/admin/s/^ *admin.*\*\*\(.*\)$/\1/p'`

if [ ! $DAVICAL_ADMIN_PASS ];
then
    echo "Something goes wrong with the database setup"
    echo "Check the logs"
    exit 1
fi

###Enable acces to Davical folder
backup $APACHE_DAVICAL_CONF
cat $APACHE_DAVICAL_CONF_TEMPLATE > $APACHE_DAVICAL_CONF
#TODO check that this conf is not too much permissive 
#TODO switch to a vhost

###Now the true configuration
backup $DAVICAL_CONF
cat $DAVICAL_CONF_TEMPLATE > $DAVICAL_CONF
sed -i "s/\@MDSSERVER\@/$MDSSERVER/" $DAVICAL_CONF
sed -i "s/\@DOMAIN\@/$MDSDOMAIN/" $DAVICAL_CONF
sed -i "s/\@SUFFIX\@/$MDSSUFFIX/" $DAVICAL_CONF

restart_service $SERVICE

echo "8The calendar and addressbook server is configured."
echo "7The temporary admin password is '$DAVICAL_ADMIN_PASS' (without the ' ')"
echo "7Remember to change it using the manadement interface http://@HOSTNAME@/davical/admin.php"


#echo "8The instant messaging service is configured."
#echo "8You can simply add users through the management interface at# http://@HOSTNAME@/mmc/. #The user's mail will be used as his Jabber ID."
#echo "7Configure clients with JID like# @B@uid@$domain@B@ #and use# @B@$hostname.$domain@B@ #as the server."
#echo "7If# @B@$hostname.$domain@B@ #is registered as a Jabber server in the DNS zone# @B@$domain@B@ #there is no need to configure the server address in clients."
