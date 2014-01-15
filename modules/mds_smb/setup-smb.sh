#!/bin/bash
# Copyright Mandriva 2009, 2010 all rights reserved

. ../functions.sh

check_mmc_configured

base_smb_template="templates/smb.conf.tpl"
smbldap_bind_template="templates/smbldap_bind.conf.tpl"
smbldap_template="templates/smbldap.conf.tpl"
mds_smb_template="templates/samba.ini.tpl"

smbdomain="$1"
smbnetbios="$2"
smbadmin="$3"
smbpass="$4"
fw_lan="$5"
fw_wan="$6"

#### Now /etc/samba/smb.conf
backup /etc/samba/smb.conf
cat $base_smb_template > /etc/samba/smb.conf
sed -i "s/\@SUFFIX\@/$MDSSUFFIX/" /etc/samba/smb.conf
sed -i "s/\@WORKGROUP\@/$smbdomain/" /etc/samba/smb.conf
sed -i "s/\@NETBIOSNAME\@/$smbnetbios/" /etc/samba/smb.conf
# handle 64bit
if [ -d /usr/lib64/mmc ]; then
    sed -i "s!/usr/lib/mmc!/usr/lib64/mmc!g" /etc/samba/smb.conf
fi

smbpasswd -w $MDSPASS
[ $? -ne 0 ] && error $"Error while setting SAMBA password." && exit 1

restart_service smb

sid=`net getlocalsid $smbdomain | cut -d ':' -f2 | cut -d ' ' -f2`

###### now /etc/smbldap-tools/smbldap.conf
backup /etc/smbldap-tools/smbldap.conf
cat $smbldap_template > /etc/smbldap-tools/smbldap.conf
sed -i "s/\@SUFFIX\@/$MDSSUFFIX/" /etc/smbldap-tools/smbldap.conf
sed -i "s/\@WORKGROUP\@/$smbdomain/" /etc/smbldap-tools/smbldap.conf
sed -i "s/\@SID\@/$sid/" /etc/smbldap-tools/smbldap.conf
sed -i "s/\@SERVER\@/$MDSSERVER/" /etc/smbldap-tools/smbldap.conf

###### now /etc/smbldap-tools/smbldap_bind.conf
backup /etc/smbldap-tools/smbldap_bind.conf
cat $smbldap_bind_template > /etc/smbldap-tools/smbldap_bind.conf
sed -i "s/\@SUFFIX\@/$MDSSUFFIX/" /etc/smbldap-tools/smbldap_bind.conf
sed -i "s/\@PASSWORD\@/$MDSPASS_E/" /etc/smbldap-tools/smbldap_bind.conf

echo -e "$smbpass\n$smbpass" | smbldap-populate -m 512 -k 512 -a "$smbadmin"
[ $? -ne 0 ] && error $"Error while populating directory." && exit 1

restart_service smb

###### now /etc/mmc/plugins/samba.ini
backup /etc/mmc/plugins/samba.ini
cat $mds_smb_template > /etc/mmc/plugins/samba.ini
sed -i "s/\@SUFFIX\@/$MDSSUFFIX/" /etc/mmc/plugins/samba.ini

sed -i "s/^defaultUserGroup = users$/defaultUserGroup = Domain Users/" /etc/mmc/plugins/base.ini
[ $? -eq 0 ] && warning $"Users are now created in the Domain Users group by default. If users were created before, they still remains in the users group."

net rpc rights grant "$smbdomain\Domain Admins" SeMachineAccountPrivilege -S $MDSSERVER -U $smbadmin%$smbpass > /dev/null 2>&1
if [ $? -ne 0 ]; then
    # Wait a little and retry once
    sleep 2
    net rpc rights grant "$smbdomain\Domain Admins" SeMachineAccountPrivilege -S $MDSSERVER -U $smbadmin%$smbpass > /dev/null 2>&1
    [ $? -ne 0 ] && error $"Failed to grant rights to the Domain Admins group" && exit 1
fi

# create directories
mkdir -p /home/samba/netlogon
setfacl -Rm group:Domain\ Admins:rwx /home/samba/netlogon
mkdir -p /home/samba/shares/public
chown "root:Domain Users" /home/samba/shares/public
mkdir -p /home/samba/profiles
chown "root:Domain Users" /home/samba/profiles
chmod 770 /home/samba/profiles

restart_service mmc-agent /var/log/mmc/mmc-agent.log

# configure the Firewall
[ $fw_lan == "on" ] && mss-add-shorewall-rule -a SMB/ACCEPT -t lan
[ $fw_wan == "on" ] && mss-add-shorewall-rule -a SMB/ACCEPT -t wan
restart_service shorewall

# confirmation
info_b $"Domain name : $smbdomain"
info_b $"Server name : $smbnetbios"
info_b $"Domain administrator : $smbadmin"
info $"- a public share is created in /home/samba/shares/public"
info $"- you can create a logon.bat script in /home/samba/netlogon"
info_b $"You can now use the management interface to manage your Windows users and shares at https://@HOSTNAME@/mmc/."

exit 0
