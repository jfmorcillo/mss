# Copyright Mandriva 2013 all rights reserved
#!/bin/bash

. ../functions.sh

check_mmc_configured

egroupware_adminUser=$1
egroupware_adminPass=$2
EGROUPWARE_POST_INST="templates/post_install.php"
mysql_password=`cat /root/.my.cnf | grep password  | sed "s/password='\(.*\)'/\1/"`
MAIL_SERV=`sqlite3 /var/lib/mss/mss-agent.db  "select * from module where name='mail';" | cut -d "|" -f1`

if [ -f "/var/www/egroupware/header.inc.php" ]; then
    rm -f /var/www/egroupware/header.inc.php
fi

mysql_do_query "DROP DATABASE IF EXISTS egroupware;"


EMAIL_SERV_CFG=
if [ ! -z $MAIL_SERV ]; then
    EMAIL_SERV_CFG="--mailserver localhost,$DOMAIN --smtpserver localhost,587,root,$MDSPASS --smtp yes,emailadmin_smtp_mandriva"
fi
php $EGROUPWARE_POST_INST --source_dir /var/www/egroupware/ --distro mandriva \
    --account-auth ldap --ldap_host 'ldaps://127.0.0.1' --ldap_suffix "$MDSSUFFIX" --ldap_admin_pw $MDSPASS \
    --db_type mysql --db_host localhost --db_pass $egroupware_adminPass  --db_root_pw $mysql_password \
    $EMAIL_SERV_CFG \
    --config_user $egroupware_adminUser --config_passwd $egroupware_adminPass --admin_user $egroupware_adminUser --admin_passwd $egroupware_adminPass
    

exit $?