#!/bin/sh

. '../functions.sh'

rootpwd=$1
auditpwd=$2

# mysql setup
mysql_prepare
mysql_get_root_password $rootpwd
if [ $? -ne 0 ]; then
    echo "2The current Mysql password is not valid."
    mysql_cleanup
    exit 1
fi
echo "Create audit database"
mysql_do_query "DROP DATABASE audit;"
mysql_do_query "CREATE DATABASE audit;"
echo "Grant privileges on database"
mysql_do_query "GRANT ALL PRIVILEGES ON audit.* TO 'audit'@'localhost' IDENTIFIED BY '$auditpwd' WITH GRANT OPTION; FLUSH PRIVILEGES;"
mysql_cleanup

# audit tables setup
audittpl="templates/base-audit.ini.tpl"

grep -q "\[audit\]" /etc/mmc/plugins/base.ini
if [ $? -ne 0 ]; then
    # first audit install
    cat $audittpl >> /etc/mmc/plugins/base.ini
    sed -i "s/\@AUDITPASSWORD\@/${auditpwd}/" /etc/mmc/plugins/base.ini
else
    # audit reconfigure
    sed -i "s/^\(dbpassword[[:space:]]\+=[[:space:]]\+\).*$/\1${auditpwd}/" /etc/mmc/plugins/base.ini
fi

mmc-helper audit init

restart_service mmc-agent /var/log/mmc/mmc-agent.log

echo 8Audit module is activated in the MDS interface : https://@HOSTNAME@/mmc/

exit 0
