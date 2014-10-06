#!/bin/bash
# Copyright Mandriva 2009, 2010 all rights reserved
if [ "`id -u`" != "0" ]; then
	echo "Error, must be root user"
	exit 1
fi

mds_base_ini="/etc/mmc/plugins/base.ini"

if [ ! -f $mds_base_ini ]; then
    echo "2MMC interface is not installed."
    echo "2Can't continue."
    exit 1
fi

mysql_rootpasswd=$1
mysql_zarafapasswd=$2
zarafa_attachments=$3
zarafa_lang=$4
zarafa_imap=$5
zarafa_ical=$6
zarafa_zpush=$7
smtpd_myhostname="$8"
# always authorize localhost
smtpd_mynetworks="127.0.0.1/32"
# add networks specified in wizard
for network in $9
do
    smtpd_mynetworks=$smtpd_mynetworks,$network
done
hostname=`echo $smtpd_myhostname | sed 's/\..*//g'`

# get ldap configuration
mdssuffix=`grep '^baseDN' $mds_base_ini | sed 's/^.*[[:space:]]\+=[[:space:]]\+//'`
mdsadmin=`grep '^rootName' $mds_base_ini | sed 's/^.*[[:space:]]\+=[[:space:]]\+//'`
mdspass=`grep '^password' $mds_base_ini | sed 's/^.*[[:space:]]\+=[[:space:]]\+//'`
mdsserver=127.0.0.1

. '../functions.sh'

if [ "`uname -m`" != "x86_64" ]; then
    # zarafa confg
    server_tpl="templates/server-32.cfg.tpl"
else
    # zarafa config
    server_tpl="templates/server-64.cfg.tpl"
fi
# postfix config
main_cf_template="templates/main.cf.tpl"
master_cf_template="templates/master.cf.tpl"
# zarafa config
server_cfg="/etc/zarafa/server.cfg"
spooler_tpl="templates/spooler.cfg.tpl"
spooler_cfg="/etc/zarafa/spooler.cfg"
ldap_tpl="templates/ldap.cfg.tpl"
ldap_cfg="/etc/zarafa/ldap.cfg"
gateway_tpl="templates/gateway.cfg.tpl"
gateway_cfg="/etc/zarafa/gateway.cfg"
ical_tpl="templates/ical.cfg.tpl"
ical_cfg="/etc/zarafa/ical.cfg"
dagent_tpl="templates/dagent.cfg.tpl"
dagent_cfg="/etc/zarafa/dagent.cfg"
userscripts="templates/userscripts"
webaccess_tpl="templates/zarafa-webaccess.conf.tpl"
zpush_tpl="templates/z-push.conf.tpl"
# mmc config
mail_ini_template="templates/mail.ini.tpl"
# postfix config
ldap_accounts_cf="templates/ldap-accounts.cf"
ldap_aliases_cf="templates/ldap-aliases.cf"
ldap_domains_cf="templates/ldap-domains.cf"
ldap_maildrop_cf="templates/ldap-maildrop.cf"
ldap_transport_cf="templates/ldap-transport.cf"
openssl_cnf_template="templates/openssl.cnf.tpl"
# amavis config
amavis_template="templates/amavisd.conf.tpl"
# spamassassin config
spamassassin_template="templates/local.cf.tpl"

# mysql setup
mysql_prepare
mysql_get_root_password ${mysql_rootpasswd}
if [ $? -ne 0 ]; then
    echo "2The current Mysql password is not valid."
    mysql_cleanup
    exit 1
fi
echo "Create zarafa database"
mysql_do_query "DROP DATABASE zarafa;"
mysql_do_query "CREATE DATABASE zarafa;"
echo "Grant privileges on database"
mysql_do_query "GRANT ALL PRIVILEGES ON zarafa.* TO 'zarafa'@'localhost' IDENTIFIED BY '${mysql_zarafapasswd}' WITH GRANT OPTION; FLUSH PRIVILEGES;"
mysql_cleanup

# tune mysql
sed -i 's!^max_allowed_packet.*$!max_allowed_packet=16M!' /etc/my.cnf

# create zarafa configuration
backup ${server_cfg}
backup ${spooler_cfg}
backup ${gateway_cfg}
backup ${ical_cfg}
backup ${dagent_cfg}
backup /etc/sysconfig/zarafa

# install locales for default lang
lang=`echo $zarafa_lang | sed 's!\([^_]*\).*$!\\1!'`
if [ "$lang" != "C" ]; then
    urpmi --auto locales-${lang}
    # set default lang for zarafa
    sed -i "s|^ZARAFA_USERSCRIPT_LOCALE=.*$|ZARAFA_USERSCRIPT_LOCALE=\"${zarafa_lang}\"|" /etc/sysconfig/zarafa
fi

# add system user zarafa for running the services
useradd -r -m zarafa

# attachments dir
if [ ! -d ${zarafa_attachments} ]; then
    mkdir -p ${zarafa_attachments}
fi
chown root.root ${zarafa_attachments}
chmod 750 ${zarafa_attachments}

# configurations
cp -f $spooler_tpl $spooler_cfg
cp -f $gateway_tpl $gateway_cfg
cp -f $dagent_tpl $dagent_cfg

cp -f $ical_tpl $ical_cfg
timezone=`grep ^ZONE /etc/sysconfig/clock | sed s'!^ZONE=\(.*\)$!\1!'`
sed -i "s!\@TIMEZONE\@!${timezone}!" $ical_cfg

cp -f $server_tpl $server_cfg
sed -i "s/\@MYSQLPASSWORD\@/${mysql_zarafapasswd}/" $server_cfg
sed -i "s!\@ATTACHMENTSPATH\@!${zarafa_attachments}!" $server_cfg

cp -f $ldap_tpl $ldap_cfg
sed -i "s/\@LDAPBINDDN\@/${mdsadmin}/" $ldap_cfg
sed -i "s/\@LDAPBINDPASSWORD\@/${mdspass}/" $ldap_cfg
sed -i "s/\@LDAPSEARCHBASE\@/${mdssuffix}/" $ldap_cfg

cp -rf $userscripts /etc/zarafa

# FIXME (packaging)
if [ -f "/etc/httpd/conf/zarafa-webaccess.conf" ]; then
    mv /etc/httpd/conf/zarafa-webaccess.conf /etc/httpd/conf/webapps.d/zarafa-webaccess.conf
fi

# z-push support
if [ "$zarafa_zpush" == "on" ]; then
    tar xzvf data/z-push-1.5.1.tar.gz -C /var/www
    chown apache.apache /var/www/z-push/state
    cp -f ${zpush_tpl} /etc/httpd/conf/webapps.d/z-push.conf
fi
# run services at boot
enable_service zarafa-server
if [ "$zarafa_imap" == "on" ]; then
    enable_service zarafa-gateway
else
    disable_service zarafa-gateway
fi
enable_service zarafa-spooler
enable_service zarafa-monitor
enable_service zarafa-dagent
if [ "$zarafa_ical" == "on" ]; then
    enable_service zarafa-ical
else
    disable_service zarafa-ical
fi

# create postfix configuration
adduser -r -g mail --uid 499 vmail > /dev/null 2>&1

backup /etc/postfix/main.cf

cp -f $main_cf_template /etc/postfix/main.cf
sed -i "s/\@FQDN\@/$smtpd_myhostname/" /etc/postfix/main.cf
sed -i "s/\@HOSTNAME\@/$hostname/" /etc/postfix/main.cf
sed -i "s!\@MYNETWORKS\@!$smtpd_mynetworks!" /etc/postfix/main.cf
# handle 64bit arch
if [ "`uname -m`" == "x86_64" ]; then
    postconf -e 'daemon_directory = /usr/lib64/postfix'
fi

backup /etc/postfix/master.cf
cp -f $master_cf_template /etc/postfix/master.cf

for template in $ldap_accounts_cf $ldap_aliases_cf $ldap_domains_cf $ldap_maildrop_cf $ldap_transport_cf
do
    newfile="/etc/postfix/`basename $template`"
    cp -f $template $newfile
    sed -i "s/\@HOST\@/$mdsserver/" $newfile
    sed -i "s/\@SUFFIX\@/$mdssuffix/" $newfile
done

# certifs gen for postfix/zarafa
cat $openssl_cnf_template > /tmp/openssl.cnf
sed -i "s/\@COMMONNAME\@/$smtpd_myhostname/" /tmp/openssl.cnf
sed -i "s/\@DOMAIN\@/$smtpd_myorigin/" /tmp/openssl.cnf
openssl req -x509 -new \
    -config /tmp/openssl.cnf \
    -out /etc/mss/ssl/smtpd.pem \
    -keyout /etc/mss/ssl/smtpd.key \
    -days 730 -nodes -batch > /dev/null 2>&1
rm -f /tmp/openssl.cnf
chmod 600 /etc/mss/ssl/smtpd.key

# add zarafa schema in LDAP
add_schema templates/zarafa.schema

# mmc conf
backup /etc/mmc/plugins/mail.ini
cp -f $mail_ini_template /etc/mmc/plugins/mail.ini
sed -i "s/\@SUFFIX\@/$mdssuffix/" /etc/mmc/plugins/mail.ini

# amavis configuration
backup /etc/amavisd/amavisd.conf
cp -f $amavis_template /etc/amavisd/amavisd.conf
sed -i "s/\@SUFFIX\@/$mdssuffix/" /etc/amavisd/amavisd.conf
sed -i "s/\@FQDN\@/$smtpd_myhostname/" /etc/amavisd/amavisd.conf
chmod 640 /etc/amavisd/amavisd.conf

# amavis / clamav
usermod -G amavis clamav
# amavis / razor
su - amavis -s /bin/sh -c 'razor-admin -d --create && razor-admin -register && razor-admin -discover' 2>&1 > /dev/null
if [ $? -eq 0 ]; then echo "0Razor configured successfully."
else
	su - amavis -s /bin/sh -c 'razor-admin -register && razor-admin -discover' 2>&1 > /dev/null
	if [ $? -eq 0 ]; then echo "0Razor configured successfully."
	else echo "1Failed to register razor. Try to run as root# : su - amavis -s /bin/sh -c 'razor-admin -register && razor-admin -discover'"
	fi
fi
# no pyzor on mandriva
# su - amavis -s /bin/sh -c 'pyzor discover'

# spamassassin
backup /etc/mail/spamassassin/local.cf
cat $spamassassin_template > /etc/mail/spamassassin/local.cf

chown zarafa.zarafa /var/log/zarafa

# restart services
restart_service mysqld
restart_service slapd
restart_service mmc-agent /var/log/mmc/mmc-agent.log
restart_service clamd
restart_service amavisd
restart_service postfix
restart_service zarafa-server /var/log/zarafa/server.cfg
if [ "$zarafa_imap" == "on" ]; then
    restart_service zarafa-gateway /var/log/zarafa/gateway.cfg
fi
restart_service zarafa-spooler /var/log/zarafa/spooler.cfg
restart_service zarafa-monitor /var/log/zarafa/monitor.cfg
restart_service zarafa-dagent /var/log/zarafa/dagent.cfg
if [ "$zarafa_ical" == "on" ]; then
    restart_service zarafa-ical /var/log/zarafa/ical.cfg
fi
restart_service httpd /var/log/httpd/error.log

echo "8Zarafa web interface is available at : http://@HOSTNAME@/webaccess/"
echo "8Mail module with Zarafa support is activated in the MDS interface : https://@HOSTNAME@/mmc/"
echo "7You can create mail domains in the MDS interface and specify mail adresses to users and groups"
echo "7You have to set zarafa attributes to users and groups from the MDS interface if you want them in zarafa"
echo "7- SSL is enabled on the smtp server"
if [ "$zarafa_imap" == "on" ]; then
    echo "7- IMAP and IMAPS protocols are enabled"
fi
if [ "$zarafa_ical" == "on" ]; then
    echo "7- iCal and CalDAV protocols are enabled. You can access calendars on http://@HOSTNAME@:8080/caldav and http://@HOSTNAME@:8080/ical with your mail client, or on port 8443 over https"
fi
if [ "$zarafa_zpush" == "on" ]; then
    echo "7- ActiveSync support is enabled"
fi
echo "7- Networks authorized to send mail without authentication : #$smtpd_mynetworks"
echo "8Make sure you have enabled mail services (SMTP 25, SMTPS 465, IMAP 143, IMAPS 993, CalDAV/iCal 8080 and 8443 (SSL)) on your firewall"

exit 0
