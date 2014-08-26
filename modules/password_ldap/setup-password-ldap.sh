#!/bin/bash
# Copyright Mandriva 2013 all rights reserved

. '../functions.sh'

check_mmc_configured

old_password=$1
new_password=$2

# changing the LDAP password
rootDN="uid=LDAP Admin, ou=System Accounts, $MDSSUFFIX"
echo "Changing password for $rootDN..."
ldappasswd -x -D "$rootDN" -h $MDSSERVER -w $old_password -s $new_password && info_b $"Password changed." || (error $"Failed to change the password."; exit 1)
sed -i "s!^password =.*!password = $new_password!" /etc/mmc/plugins/base.ini || (error $"Failed to change the password."; ldappasswd -x -D "$rootDN" -h $MDSSERVER -w $new_password -s $old_password; exit 1)

restart_service mmc-agent
