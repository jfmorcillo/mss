#!/bin/bash
# Copyright Mandriva 2009, 2010 all rights reserved

if [ "`id -u`" != "0" ]; then
	echo "Error, must be root user"
	exit 1
fi

. '../functions.sh'

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

myfqdn=`hostname -f`
if [ -z "$myfqdn" ]; then
	myfqdn="localhost"
fi
mydomain=$1
mypass_e=`escape_sed $2`
mypass=$2
ppolicy=$3

# MDS schemas
add_schema /usr/share/doc/python-mmc-base/contrib/ldap/dhcp.schema
add_schema /usr/share/doc/python-mmc-base/contrib/ldap/dnszone.schema
add_schema /usr/share/doc/python-mmc-base/contrib/ldap/mail.schema
add_schema /usr/share/doc/python-mmc-base/contrib/ldap/mmc.schema

mysuffix=`calc_suffix $mydomain`
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

## ppolicy
#backup /etc/mmc/plugins/ppolicy.ini
#cat $ppolicy_template > /etc/mmc/plugins/ppolicy.ini
#sed -i "s/\@SUFFIX\@/$mysuffix/" /etc/mmc/plugins/ppolicy.ini
#if [ "$ppolicy" == "on" ]; then
#    sed -i "s/\@DISABLE\@/0/" /etc/mmc/plugins/ppolicy.ini
#else
#    sed -i "s/\@DISABLE\@/1/" /etc/mmc/plugins/ppolicy.ini
#fi

# now, /etc/openldap/ldap.conf
myldapconf=`make_temp`
cat /etc/openldap/ldap.conf | \
	sed -e "s/^BASE[[:blank:]]\+.*/BASE $mysuffix/g;\
	s/^HOST[[:blank:]]\+.*/HOST $myfqdn/g;\
	s@^URI[[:blank:]]\+.*@URI ldap://$myfqdn@g" \
	> $myldapconf
if ! grep -qE '^(HOST|URI)' $myldapconf; then
	echo "URI ldap://$myfqdn" >> $myldapconf
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
	s/@DC@/${mydomain%%.[a-zA-Z0-9]*}/g;\
	s/@DOMAIN@/${mydomain}/g;\
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

restart_service ldap
restart_service mmc-agent /var/log/mmc/mmc-agent.log
restart_service httpd

echo "8The MBS management interface is configured."
echo "8You can log in the MBS management interface at http://@HOSTNAME@/mmc/ and start adding users and groups."
echo "8Administrator name : root"
echo "8Administrator password : #$mypass"

exit 0
