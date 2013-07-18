# Copyright Mandriva 2013 all rights reserved
#!/bin/bash

. ../functions.sh

check_mmc_configured

egroupware_adminUser=$1
egroupware_adminPass=$2
EGROUPWARE_POST_INST="templates/post_install.php"
mysql_password=`cat /root/.my.cnf | grep password  | sed "s/password='\(.*\)'/\1/"`
MAIL_SERV=$(echo "select name from module where name='mds_mail';" | sqlite3 /var/lib/mss/mss-agent.db)
EGROUPWARE_CONF_FILE="/etc/httpd/conf/webapps.d/egroupware.conf"

### Clean generated resource before running eGroupware configuration
if [ -f "/var/www/egroupware/header.inc.php" ]; then
    rm -f /var/www/egroupware/header.inc.php
fi

#TODO: check that the user that will be created as egroupware admin does not exit.
# In the case where a local user already exists the script will silently fail to 
# create the admin.

### Email service configuration
EMAIL_SERV_CFG=
if [ ! -z $MAIL_SERV ]; then
    EMAIL_SERV_CFG="--mailserver localhost,imaps,$DOMAIN,vmailmgr --smtpserver localhost,25,,,yes --imap root,$MDSPASS,emailadmin_dovecot"
fi
php $EGROUPWARE_POST_INST --verbose --source_dir /var/www/egroupware/ --distro mandriva \
    --account-auth ldap --ldap_host 'ldaps://127.0.0.1' --ldap_suffix "$MDSSUFFIX" --ldap_admin_pw $MDSPASS \
    --db_type mysql --db_host localhost --db_pass $egroupware_adminPass  --db_root_pw $mysql_password \
    $EMAIL_SERV_CFG \
    --config_user $egroupware_adminUser --config_passwd $egroupware_adminPass --admin_user $egroupware_adminUser --admin_passwd $egroupware_adminPass
# @TODO: anonymous configuration to authorize notifications

# Fix path to jpgraph
if [ ! -d /var/www/jpgraph ]; then
    mkdir -p /var/www/jpgraph
    cp -r /usr/share/php/jpgraph /var/www/jpgraph/src
    backup $EGROUPWARE_CONF_FILE
    sed -i 's!/usr/share/jpgraph!/var/www/jpgraph!' $EGROUPWARE_CONF_FILE
    #FIXES mission version file
    echo "Version: v3.5.0b1" > /var/www/jpgraph/VERSION
    chown root:apache -R /var/www/jpgraph
fi

# Fix permissions
chmod 640 /var/www/egroupware/header.inc.php

chown root:apache -R /var/www/egroupware

restart_service http

info_b $"eGroupware is installed and configured. Your user in the LDAP may belong to Default group to benefit from default authorisation in the eGroupware application."
info $"You can access eGroupware at https://$FQDN/egroupware"
info $"EGroupware administrator is '$egroupware_adminUser' and password is '$egroupware_adminPass'"

exit $?