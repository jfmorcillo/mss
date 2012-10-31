#!/bin/bash
# Copyright Mandriva 2009, 2010 all rights reserved

. '../functions.sh'

check_root

SLAPTEST="/usr/sbin/slaptest"
SLAPADD="/usr/sbin/slapadd"
SLAPPASSWD="/usr/sbin/slappasswd"

if [ "`uname -m`" != "x86_64" ]; then
	slapd_conf_template="templates/slapd-32.conf.tpl"
    base_mds_template="templates/base-32.ini.tpl"
else
	slapd_conf_template="templates/slapd-64.conf.tpl"
    base_mds_template="templates/base-64.ini.tpl"
fi

ppolicy_template="templates/ppolicy.ini.tpl"
base_ldif_template="templates/init.ldif.tpl"
acl_template="templates/mandriva-dit-access.conf.tpl"
acl_file="/etc/openldap/mandriva-dit-access.conf"
ldap_conf_template="templates/ldap.conf.tpl"
nsswitch_template="templates/nsswitch.conf.tpl"

mypass=$1
mypass_e=`escape_sed $mypass`
mysuffix=`calc_suffix $DOMAIN`
fw_lan=$2
fw_wan=$3

# MDS schemas
add_schema /usr/share/doc/python-mmc-base/contrib/ldap/dhcp.schema
add_schema /usr/share/doc/python-mmc-base/contrib/ldap/dnszone.schema
add_schema /usr/share/doc/python-mmc-base/contrib/ldap/mail.schema
add_schema /usr/share/doc/python-mmc-base/contrib/ldap/mmc.schema

# Generate LDAP password
pass=`$SLAPPASSWD -h {SSHA} -s "$mypass"`
if [ "$?" -ne "0" ]; then echo "1Error at generating password"; exit 1
else echo "0Password successfully generated"
fi

myslapdconf=`make_temp`
cat $slapd_conf_template > $myslapdconf
sed -i "s/\@SUFFIX\@/$mysuffix/" $myslapdconf
chmod 0640 $myslapdconf
chgrp ldap $myslapdconf

backup /etc/mmc/plugins/base.ini

#### Now /etc/mmc/plugins/base.ini
cat $base_mds_template > /etc/mmc/plugins/base.ini
sed -i "s/\@SUFFIX\@/$mysuffix/" /etc/mmc/plugins/base.ini
sed -i "s/\@PASSWORD\@/$mypass_e/" /etc/mmc/plugins/base.ini
mkdir /home/archives > /dev/null 2>&1

# now, /etc/openldap/ldap.conf
myldapconf=`make_temp`
cat /etc/openldap/ldap.conf | \
	sed -e "s/^BASE[[:blank:]]\+.*/BASE ${mysuffix}/g;\
	s/^HOST[[:blank:]]\+.*/HOST ${SERVER}/g;\
	s@^URI[[:blank:]]\+.*@URI ldap://${SERVER}@g" \
	> $myldapconf
if ! grep -qE '^(HOST|URI)' $myldapconf; then
	echo "URI ldap://${SERVER}" >> $myldapconf
fi
if ! grep -qE '^BASE' $myldapconf; then
	echo "BASE $mysuffix" >> $myldapconf
fi
chmod 0644 $myldapconf

# ACL file
cat $acl_template | sed -e "s/@SUFFIX@/$mysuffix/g" > $acl_file
chmod 0640 $acl_file
chgrp ldap $acl_file

$SLAPTEST -u -f $myslapdconf > /dev/null 2>&1
if [ $? -ne 0 ]; then
	echo "2OpenLDAP configuration file was generated with errors."
	echo "2Aborting. File used was# $myslapdconf"
	rm -f $myldapconf
	exit 1
else
    echo "0OpenLDAP configuration file successfully generated."
fi

# LDIF
myldif=`make_temp`
cat $base_ldif_template | sed -e "\
	s/@SUFFIX@/$mysuffix/g;\
	s/@DC@/${DOMAIN%%.[a-zA-Z0-9]*}/g;\
	s/@DOMAIN@/${DOMAIN}/g;\
	s|@ldapadmin_password@|$pass|g" > $myldif

# dry run first
$SLAPADD -u -f $myslapdconf < $myldif
if [ $? -ne 0 ]; then
	echo "2Database loading failed during test run."
	echo "2Ldif file used:# $myldif"
	echo "2slapd.conf file used:# $myslapdconf"
	rm -f $myldapconf
	exit 1
else
    echo "0Database loading test successfull."
fi

# let's go for real now
stop_service ldap
stop_service mmc-agent /var/log/mmc/mmc-agent.log

backup_db=`clean_database /var/lib/ldap`
backup_slapd_conf=`mybackup /etc/openldap/slapd.conf`
backup_ldap_conf=`mybackup /etc/openldap/ldap.conf`
echo "0Writing# /etc/openldap/slapd.conf #and# /etc/openldap/ldap.conf..."
cat $myslapdconf > /etc/openldap/slapd.conf; rm -f $myslapdconf
cat $myldapconf > /etc/openldap/ldap.conf; rm -f $myldapconf

echo "0Loading database..."
$SLAPADD < $myldif
if [ $? -ne 0 ]; then
	echo "2Something went wrong while initializing the database"
	echo "2Aborting. Your previous database is at# $backup_db"
	echo "2Your original /etc/openldap/{slapd,ldap}.conf files"
	echo "2were backed up as# $backup_slapd_conf #and"
	echo "2$backup_ldap_conf, respectively."
	exit 1
else
    echo "0Database loaded successfully."
    echo "0Your previous database directory has been backed up as# $backup_db."
fi

backup /etc/nsswitch.conf
cat $nsswitch_template > /etc/nsswitch.conf
backup /etc/ldap.conf
cat $ldap_conf_template > /etc/ldap.conf
sed -i "s/\@SUFFIX\@/$mysuffix/" /etc/ldap.conf
sed -i "s/\@SERVER\@/$SERVER/" /etc/ldap.conf
if [ $? -eq 0 ]; then echo "0lib nss-ldap configuration done. (/etc/ldap.conf and /etc/nsswitch.conf updated)";
else echo "2Error while configuring lib nss-ldap. (/etc/ldap.conf and /etc/nsswitch.conf)"; exit 1
fi

# enable modules
sed -i 's/disable = 1/disable = 0/' /etc/mmc/plugins/services.ini
sed -i 's/disable = 1/disable = 0/' /etc/mmc/plugins/dashboard.ini

# http -> https redirection
https_redirect mmc /etc/httpd/conf/webapps.d/mmc.conf

# add shorewall plugin...
cp -r plugins/shorewall /usr/lib/python2.7/site-packages/mmc/plugins/
cp -r modules/shorewall /usr/share/mmc/modules/
cp plugins/shorewall.ini /etc/mmc/plugins/

restart_service ldap
restart_service mmc-agent /var/log/mmc/mmc-agent.log
restart_service httpd
restart_service mmc-agent /var/log/mmc/mmc-agent.log

# configure the Firewall
[ $fw_lan == "on" ] && mss-add-shorewall-rule -a Web/ACCEPT -t lan
[ $fw_wan == "on" ] && mss-add-shorewall-rule -a Web/ACCEPT -t wan

echo "8The MBS management interface is configured."
echo "8You can log in the MBS management interface at https://@HOSTNAME@/mmc/ and start adding users and groups."
echo "8Administrator name : root"
echo "8Administrator password : #$mypass"

exit 0
