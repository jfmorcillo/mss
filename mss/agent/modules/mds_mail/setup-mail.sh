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

mdssuffix=`grep '^baseDN' $mds_base_ini | sed 's/^.*[[:space:]]\+=[[:space:]]\+//'`
mdspass=`grep '^password' $mds_base_ini | sed 's/^.*[[:space:]]\+=[[:space:]]\+//'`
mdsserver=127.0.0.1

. '../functions.sh'

if [ "`uname -m`" != "x86_64" ]; then
    main_cf_template="templates/main-32.cf.tpl"
    master_cf_template="templates/master-32.cf.tpl"
else
    main_cf_template="templates/main-64.cf.tpl"
    master_cf_template="templates/master-64.cf.tpl"
fi

mail_ini_template="templates/mail.ini.tpl"
dovecot_ldap_template="templates/dovecot-ldap.conf.tpl"
dovecot_template="templates/dovecot.conf.tpl"
ldap_accounts_cf_template="templates/ldap-accounts.cf.tpl"
ldap_aliases_cf="templates/ldap-aliases.cf.tpl"
ldap_domains_cf="templates/ldap-domains.cf.tpl"
ldap_maildrop_cf="templates/ldap-maildrop.cf.tpl"
ldap_transport_cf="templates/ldap-transport.cf.tpl"
openssl_cnf_template="templates/openssl.cnf.tpl"
amavis_template="templates/amavisd.conf.tpl"
spamassassin_template="templates/local.cf.tpl"

smtpd_myhostname="$1"
# always authorize localhost
smtpd_mynetworks="127.0.0.1/32"
# add networks specified in wizard
for network in $2
do
    smtpd_mynetworks=$smtpd_mynetworks,$network
done
popimap_proto="$3"

hostname=`echo $smtpd_myhostname | sed 's/\..*//g'`

# postfix
backup /etc/postfix/main.cf
cat $main_cf_template > /etc/postfix/main.cf
sed -i "s/\@FQDN\@/$smtpd_myhostname/" /etc/postfix/main.cf
sed -i "s/\@HOSTNAME\@/$hostname/" /etc/postfix/main.cf
sed -i "s!\@MYNETWORKS\@!$smtpd_mynetworks!" /etc/postfix/main.cf

backup /etc/postfix/master.cf
cat $master_cf_template > /etc/postfix/master.cf

for template in $ldap_accounts_cf_template $ldap_aliases_cf $ldap_domains_cf $ldap_maildrop_cf $ldap_transport_cf
do
    newfile="/etc/postfix/`basename $template`"
    cat $template > $newfile
    sed -i "s/\@HOST\@/$mdsserver/" $newfile
    sed -i "s/\@SUFFIX\@/$mdssuffix/" $newfile
done

# dovecot
backup /etc/dovecot.conf
cat $dovecot_template > /etc/dovecot.conf
sed -i "s/\@PROTOCOLS\@/$popimap_proto/" /etc/dovecot.conf

if [ -f /etc/dovecot-ldap.conf ]; 
    then backup /etc/dovecot-ldap.conf
fi
cat $dovecot_ldap_template > /etc/dovecot-ldap.conf
sed -i "s/\@SUFFIX\@/$mdssuffix/" /etc/dovecot-ldap.conf
sed -i "s/\@HOST\@/$mdsserver/" /etc/dovecot-ldap.conf

# certifs gen
cat $openssl_cnf_template > /tmp/openssl.cnf
sed -i "s/\@COMMONNAME\@/$smtpd_myhostname.$smptd_myorigin/" /tmp/openssl.cnf
sed -i "s/\@DOMAIN\@/$smptd_myorigin/" /tmp/openssl.cnf

mkdir -p /etc/ssl/mmc-wizard/certs
mkdir -p /etc/ssl/mmc-wizard/private
openssl req -x509 -new \
    -config /tmp/openssl.cnf \
    -out /etc/ssl/mmc-wizard/certs/smtpd.pem \
    -keyout /etc/ssl/mmc-wizard/private/smtpd.key \
    -days 730 -nodes -batch > /dev/null 2>&1
rm -f /tmp/openssl.cnf

chmod 600 /etc/ssl/mmc-wizard/private/smtpd.key

adduser -r -g mail --uid 499 vmail > /dev/null 2>&1
mkdir -p /home/vmail > /dev/null 2>&1
chown vmail:mail /home/vmail

# mmc conf
backup /etc/mmc/plugins/mail.ini
cat $mail_ini_template > /etc/mmc/plugins/mail.ini
sed -i "s/\@SUFFIX\@/$mdssuffix/" /etc/mmc/plugins/mail.ini

# amavis configuration
backup /etc/amavisd/amavisd.conf
cat $amavis_template > /etc/amavisd/amavisd.conf
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
# no pyzor on mandriva :(
# su - amavis -s /bin/sh -c 'pyzor discover'

# spamassassin
backup /etc/mail/spamassassin/local.cf
cat $spamassassin_template > /etc/mail/spamassassin/local.cf

/sbin/service mmc-agent restart > /dev/null 2>&1
if [ $? -eq 0 ]; then echo "0Service #MMC# reloaded succesfully."
else echo "2Service #MMC# fails restarting. Check #/var/log/mmc/mmc-agent.log"; sleep 1; exit 1
fi

/sbin/service amavisd restart > /dev/null 2>&1
if [ $? -eq 0 ]; then echo "0Service #amavis# reloaded succesfully."
else echo "2Service #amavis# fails restarting. Check #/var/log/syslog"; sleep 1; exit 1
fi

/sbin/service clamd restart > /dev/null 2>&1
if [ $? -eq 0 ]; then echo "0Service #clamd# reloaded succesfully."
else echo "2Service #clamd# fails restarting. Check #/var/log/syslog"; sleep 1; exit 1
fi

/sbin/service postfix restart > /dev/null 2>&1
if [ $? -eq 0 ]; then echo "0Service #postfix# reloaded succesfully."
else echo "2Service #postfix# fails restarting. Check #/var/log/syslog"; sleep 1; exit 1
fi

/sbin/service dovecot restart > /dev/null 2>&1
if [ $? -eq 0 ]; then echo "0Service #dovecot# reloaded succesfully."
else echo "2Service #dovecot# fails restarting. Check #/var/log/syslog"; sleep 1; exit 1
fi

echo "8Mail module is activated in the MDS interface : http://@HOSTNAME@/mmc/"
echo "7You can create mail domains in the MDS interface and specify mail adresses to users and groups."
echo "7- mails are stored in /home/vmail/user/Maildir"
echo "7- SSL is enabled on the smtp server"
echo "7- Non-SSL connexions on external interfaces are disabled by default on the IMAP server"
echo "7- Networks authorized to send mail without authentication : #$smtpd_mynetworks" 
echo "8Make sure you have enabled mail services (SMTP 25, SMTPS 465, POPS 995, IMAPS 993) on your firewall."

exit 0
