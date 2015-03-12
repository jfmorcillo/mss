#!/bin/bash
# Copyright Mandriva 2009, 2010 all rights reserved

. '../functions.sh'

check_mmc_configured

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
ldap_accounts_cf="templates/ldap-accounts.cf"
ldap_aliases_cf="templates/ldap-aliases.cf"
ldap_valiases_cf="templates/ldap-valiases.cf"
ldap_domains_cf="templates/ldap-domains.cf"
ldap_maildrop_cf="templates/ldap-maildrop.cf"
ldap_transport_cf="templates/ldap-transport.cf"
amavis_template="templates/amavisd.conf.tpl"
spamassassin_template="templates/local.cf.tpl"

# always authorize localhost
smtpd_mynetworks="127.0.0.1/32"
# add networks specified in wizard
for network in $1
do
    smtpd_mynetworks=$smtpd_mynetworks,$network
done
popimap_proto="$2"
fw_lan="$3"
fw_wan="$4"

# LDAP schema
schema=/usr/share/doc/mmc/contrib/mail/mail.schema
[ -f $schema ] && add_schema $schema || add_schema templates/mail.schema

# postfix
backup /etc/postfix/main.cf
cat $main_cf_template > /etc/postfix/main.cf
sed -i "s/\@FQDN\@/$FQDN/" /etc/postfix/main.cf
sed -i "s/\@HOSTNAME\@/$HOST/" /etc/postfix/main.cf
sed -i "s!\@MYNETWORKS\@!$smtpd_mynetworks!" /etc/postfix/main.cf

backup /etc/postfix/master.cf
cat $master_cf_template > /etc/postfix/master.cf

for template in $ldap_accounts_cf $ldap_aliases_cf $ldap_valiases_cf $ldap_domains_cf $ldap_maildrop_cf $ldap_transport_cf
do
    newfile="/etc/postfix/`basename $template`"
    cat $template > $newfile
    sed -i "s/\@HOST\@/$MDSSERVER/" $newfile
    sed -i "s/\@SUFFIX\@/$MDSSUFFIX/" $newfile
done

# dovecot
backup /etc/dovecot.conf
cat $dovecot_template > /etc/dovecot.conf
sed -i "s/\@PROTOCOLS\@/$popimap_proto/" /etc/dovecot.conf

if [ -f /etc/dovecot-ldap.conf ];
    then backup /etc/dovecot-ldap.conf
fi
cat $dovecot_ldap_template > /etc/dovecot-ldap.conf
sed -i "s/\@SUFFIX\@/$MDSSUFFIX/" /etc/dovecot-ldap.conf
sed -i "s/\@HOST\@/$MDSSERVER/" /etc/dovecot-ldap.conf

adduser -r -g mail --uid 30 vmail > /dev/null 2>&1
mkdir -p /home/vmail > /dev/null 2>&1
chown vmail:mail /home/vmail

# mmc conf
backup /etc/mmc/plugins/mail.ini
cat $mail_ini_template > /etc/mmc/plugins/mail.ini

# amavis configuration
backup /etc/amavisd/amavisd.conf
cat $amavis_template > /etc/amavisd/amavisd.conf
sed -i "s/\@SUFFIX\@/$MDSSUFFIX/" /etc/amavisd/amavisd.conf
sed -i "s/\@FQDN\@/$FQDN/" /etc/amavisd/amavisd.conf

chmod 640 /etc/amavisd/amavisd.conf

# amavis / clamav
usermod -G amavis clamav
# amavis / razor
su - amavis -s /bin/sh -c 'razor-admin -d --create && razor-admin -register && razor-admin -discover' 2>&1 > /dev/null
if [ $? -ne 0 ]; then
	su - amavis -s /bin/sh -c 'razor-admin -register && razor-admin -discover' 2>&1 > /dev/null
	[ $? -ne 0 ] && warning $"Failed to register razor. Try to run as root later : su - amavis -s /bin/sh -c 'razor-admin -register && razor-admin -discover'"
fi
# no pyzor on mandriva :(
# su - amavis -s /bin/sh -c 'pyzor discover'

# spamassassin
backup /etc/mail/spamassassin/local.cf
cat $spamassassin_template > /etc/mail/spamassassin/local.cf

restart_service mmc-agent /var/log/mmc/mmc-agent.log

# add the default mail domain
python add_domain.py $DOMAIN

restart_service amavisd
restart_service clamd
restart_service postfix
restart_service dovecot

# spamassassin is run by amavis
disable_service spamassassin

function add_rules() {
    mss-add-shorewall-rule -a SMTP/ACCEPT -t $1
    mss-add-shorewall-rule -a SMTPS/ACCEPT -t $1
    [[ "$popimap_proto" =~ "imaps" ]] && mss-add-shorewall-rule -a IMAPS/ACCEPT -t $1
    [[ "$popimap_proto" =~ "pop3s" ]] && mss-add-shorewall-rule -a POP3S/ACCEPT -t $1
}

# configure the Firewall
[ $fw_lan == "on" ] && add_rules lan
[ $fw_wan == "on" ] && add_rules wan
restart_service shorewall

info_b $"The mail service is configured."
info_b $"You can add mail addresses and aliases to your users through the management interface at https://@HOSTNAME@/mmc/."
info $"- the mail domain $DOMAIN has been created"
info $"- SSL is enabled on the SMTP server"
info_b $"- Non-SSL connexions are disabled by default on the IMAP/POP3 server"
info $"- Networks authorized to send mail without authentication : $smtpd_mynetworks"

exit 0
