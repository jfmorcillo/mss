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

if [ $? -eq 0 ]; then echo "0SAMBA configuration done. (/etc/samba/smb.conf updated)";
else echo "2Error while configuring SAMBA. (/etc/samba/smb.conf)"; exit 1
fi

smbpasswd -w $MDSPASS
if [ $? -eq 0 ]; then echo "0SAMBA password set.";
else echo "2Error while setting SAMBA password. (smbpasswd)"; exit 1
fi

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
if [ $? -eq 0 ]; then echo "0smbldap-lools configuration done. (/etc/smbldap-tools/smbldap.conf and /etc/smbldap-tools/smbldap_bind.conf updated)";
else echo "2Error while configuring smbldap-lools. (/etc/smbldap-tools/smbldap.conf and /etc/smbldap-tools/smbldap_bind.conf)"; exit 1
fi

echo -e "$smbpass\n$smbpass" | smbldap-populate -m 512 -k 512 -a "$smbadmin"
if [ $? -eq 0 ]; then echo "0Directory populated for SAMBA.";
else echo "2Error while populating directory.# (smbldap-populate -m 512 -k 512 -a $smbadmin)"; exit 1
fi

restart_service smb

###### now /etc/mmc/plugins/samba.ini
backup /etc/mmc/plugins/samba.ini
cat $mds_smb_template > /etc/mmc/plugins/samba.ini
sed -i "s/\@SUFFIX\@/$MDSSUFFIX/" /etc/mmc/plugins/samba.ini
if [ $? -eq 0 ]; then echo "0MDS SAMBA configuration done.";
else echo "2Error while configuring MDS SAMBA module."; exit 1
fi

sed -i "s/^defaultUserGroup = users$/defaultUserGroup = Domain Users/" /etc/mmc/plugins/base.ini
if [ $? -eq 0 ]; then echo "1Users are now created in the Domain Users group by default. If users were created, they still remains in the users group.";
fi

restart_service mmc-agent /var/log/mmc/mmc-agent.log

net rpc rights grant "$smbdomain\Domain Admins" SeMachineAccountPrivilege -S $MDSSERVER -U $smbadmin%$smbpass > /dev/null 2>&1
if [ $? -eq 0 ]; then echo "0Successfully granted rights for Domain Admins group."
else echo "2Failed granted rigths for Domain Admins group"; exit 1
fi

# create directories
mkdir -p /home/samba/netlogon
mkdir -p /home/samba/shares/public
chown "root:Domain Users" /home/samba/shares/public
mkdir -p /home/samba/profiles
chown "root:Domain Users" /home/samba/profiles
chmod 770 /home/samba/profiles

# ACL test
touch /home/samba/test
setfacl -m g:"Domain Users":rx /home/samba/test > /dev/null 2>&1
if [ $? -ne 0 ]; then 
    echo "1Your filesystem does not support ACL. You won't be able to set ACLs on SAMBA shares."
    echo "1For ext3 filesystems you have to add the acl option in /etc/fstab."
else 
    echo "0Acls supported by filesystem."
fi
rm -f /home/samba/test

# confirmation
echo "8Domain name :# $smbdomain"
echo "8Server name :# $smbnetbios"
echo "8Domain administrator :# $smbadmin"
echo "7- a public share is created in /home/samba/shares/public"
echo "7- you can create a logon.bat script in /home/samba/netlogon"
echo "8Make sure you have enabled SAMBA services on your firewall."
echo "8You can now use the management interface to manage your Windows users and shares at http://@HOSTNAME@/mmc/."

exit 0
