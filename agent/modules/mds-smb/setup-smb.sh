#!/bin/bash
# Copyright Mandriva 2009, 2010 all rights reserved
if [ "`id -u`" != "0" ]; then
	echo "1Error, must be root user"
	exit 1
fi

. '/usr/share/mmc-wizard/dit-mds/functions.sh'

base_smb_template="/usr/share/mmc-wizard/dit-mds/mandriva-setup-smb-templates/mandriva-mds-smb-template.conf"
smbldap_bind_template="/usr/share/mmc-wizard/dit-mds/mandriva-setup-smb-templates/mandriva-mds-smbldap_bind-template.conf"
smbldap_template="/usr/share/mmc-wizard/dit-mds/mandriva-setup-smb-templates/mandriva-mds-smbldap-template.conf"
mds_smb_template="/usr/share/mmc-wizard/dit-mds/mandriva-setup-smb-templates/mandriva-mds-samba-template.conf"
ldap_conf_template="/usr/share/mmc-wizard/dit-mds/mandriva-setup-smb-templates/mandriva-mds-ldapconf-template.conf"
nsswitch_template="/usr/share/mmc-wizard/dit-mds/mandriva-setup-smb-templates/mandriva-mds-nsswitch-template.conf"

mydomain="$1"
mypass="$2"
workgroup="$3"
netbiosname="$4"
server="$5"
smbpass="$6"

# first, slapd.conf
myslapdconf=`make_temp`
mysuffix=`calc_suffix $mydomain`

#### Now /etc/samba/smb.conf
backup /etc/samba/smb.conf
cat $base_smb_template > /etc/samba/smb.conf
sed -i "s/\@SUFFIX\@/$mysuffix/" /etc/samba/smb.conf
sed -i "s/\@WORKGROUP\@/$workgroup/" /etc/samba/smb.conf
sed -i "s/\@NETBIOSNAME\@/$netbiosname/" /etc/samba/smb.conf
if [ $? -eq 0 ]; then echo "0Samba configuration done. (/etc/samba/smb.conf updated)";
else echo "2Error while configuring Samba. (/etc/samba/smb.conf)"; exit 1
fi

smbpasswd -w $mypass
if [ $? -eq 0 ]; then echo "0Samba password set.";
else echo "2Error while setting Samba password. (smbpasswd)"; exit 1
fi

/sbin/service smb restart > /dev/null 2>&1
if [ $? -eq 0 ]; then echo "0Service Samba reloaded succesfully."
else echo "2Service Samba fails restarting."; exit 1
fi

sid=`net getlocalsid $workgroup | cut -d ':' -f2 | cut -d ' ' -f2`

backup /etc/nsswitch.conf
cat $nsswitch_template > /etc/nsswitch.conf
backup /etc/ldap.conf
cat $ldap_conf_template > /etc/ldap.conf
sed -i "s/\@SUFFIX\@/$mysuffix/" /etc/ldap.conf
sed -i "s/\@SERVER\@/$server/" /etc/ldap.conf
if [ $? -eq 0 ]; then echo "0lib nss-ldap configuration done. (/etc/ldap.conf and /etc/nsswitch.conf updated)";
else echo "2Error while configuring lib nss-ldap. (/etc/ldap.conf and /etc/nsswitch.conf)"; exit 1
fi

###### now /etc/smbldap-tools/smbldap.conf
backup /etc/smbldap-tools/smbldap.conf
cat $smbldap_template > /etc/smbldap-tools/smbldap.conf
sed -i "s/\@SUFFIX\@/$mysuffix/" /etc/smbldap-tools/smbldap.conf
sed -i "s/\@WORKGROUP\@/$workgroup/" /etc/smbldap-tools/smbldap.conf
sed -i "s/\@SID\@/$sid/" /etc/smbldap-tools/smbldap.conf
sed -i "s/\@SERVER\@/$server/" /etc/smbldap-tools/smbldap.conf

###### now /etc/smbldap-tools/smbldap_bind.conf
backup /etc/smbldap-tools/smbldap_bind.conf
cat $smbldap_bind_template > /etc/smbldap-tools/smbldap_bind.conf 
sed -i "s/\@SUFFIX\@/$mysuffix/" /etc/smbldap-tools/smbldap_bind.conf
sed -i "s/\@PASSWORD\@/$mypass/" /etc/smbldap-tools/smbldap_bind.conf
if [ $? -eq 0 ]; then echo "0smbldap-lools configuration done. (/etc/smbldap-tools/smbldap.conf and /etc/smbldap-tools/smbldap_bind.conf updated)";
else echo "2Error while configuring smbldap-lools. (/etc/smbldap-tools/smbldap.conf and /etc/smbldap-tools/smbldap_bind.conf)"; exit 1
fi

echo -e "$smbpass\n$smbpass" | smbldap-populate -m 512 -k 512 -a admin
if [ $? -eq 0 ]; then echo "0Directory populated for Samba.";
else echo "2Error while populating directory. (smbldap-populate -m 512 -k 512 -a admin)"; exit 1
fi

/sbin/service smb restart > /dev/null 2>&1
if [ $? -eq 0 ]; then echo "0Service Samba reloaded succesfully."
else echo "2Service Samba fails restarting."; exit 1
fi

###### now /etc/mmc/plugins/samba.ini
backup /etc/mmc/plugins/samba.ini
cat $mds_smb_template > /etc/mmc/plugins/samba.ini
sed -i "s/\@SUFFIX\@/$mysuffix/" /etc/mmc/plugins/samba.ini
if [ $? -eq 0 ]; then echo "0MDS Samba configuration done.";
else echo "2Error while configuring MDS Samba module."; exit 1
fi

sed -i "s/^defaultUserGroup = users$/defaultUserGroup = Domain Users/" /etc/mmc/plugins/base.ini
if [ $? -eq 0 ]; then echo "1Users are now created in the Domain Users group by default. If users were created, they still remains in the users group.";
fi

/sbin/service mmc-agent restart > /dev/null 2>&1
if [ $? -eq 0 ]; then echo "0Service MMC reloaded succesfully."
else echo "2Service MMC fails restarting. Check /var/log/mmc/mmc-agent.log"; exit 1
fi

net rpc rights grant "$workgroup\Domain Admins" SeMachineAccountPrivilege -S "127.0.0.1" -U admin%$smbpass > /dev/null 2>&1
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
    echo "1Your filesystem does not support ACL. You won't be able to set ACLs on Samba shares."
    echo "1For ext3 filesystems you have to add the acl option in /etc/fstab."
else 
    echo "0Acls supported by filesystem."
fi
rm -f /home/samba/test

# confirmation
echo "8Domain name : #$workgroup"
echo "8Server name : #$netbiosname"
echo 8Domain admin name : admin
## echo "8Domain admin password : #$smbpass"
echo 7- a public share is created in /home/samba/shares/public
echo 7- you can create a logon.bat script in /home/samba/netlogon
echo 8Make sure you have enabled Samba services on your firewall.
echo '8You can now use the MDS interface to manage your Windows users and shares (http://@HOSTNAME@/mmc/).'

echo 1Profiles are disabled by default.
echo 1- edit /etc/samba/smb.conf manually to activate them.
