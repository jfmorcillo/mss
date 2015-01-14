#!/bin/bash
# Copyright Mandriva 2014 all rights reserved

#Debug mode
#set -x

. '../functions.sh'

check_mmc_configured

fw_lan=$1
fw_wan=$2
asterisk_lang=$3

# Import LDAP schema
add_schema ldap/asterisk.schema
restart_service slapd

# Import LDIF file
echo "
dn: ou=asterisk,$MDSSUFFIX
objectClass: organizationalUnit
ou: asterisk

dn: ou=extensions,ou=asterisk,$MDSSUFFIX
objectClass: organizationalUnit
ou: extensions

dn: ou=voicemail,ou=asterisk,$MDSSUFFIX
objectClass: organizationalUnit
ou: voicemail

dn: cn=*97-1,ou=extensions,ou=asterisk,$MDSSUFFIX
objectClass: top
objectClass: inetOrgPerson
objectClass: AsteriskExtension
AstApplication: Voicemailmain
AstApplicationData: \${CALLERID(num)}
AstContext: internal
AstExtension: *97
AstPriority: 1
cn: *97-1
sn: *97-1

dn: cn=*98-1,ou=extensions,ou=asterisk,$MDSSUFFIX
objectClass: top
objectClass: inetOrgPerson
objectClass: AsteriskExtension
AstApplication: Voicemailmain
AstContext: internal
AstExtension: *98
AstPriority: 1
cn: *98-1
sn: *98-1

" | ldapadd -x -c -D "uid=LDAP Admin,ou=System Accounts,$MDSSUFFIX" -w $MDSPASS

ASTERISK_SIP="/etc/asterisk/sip.conf"
ASTERISK_EXTENSIONS="/etc/asterisk/extensions.conf"
ASTERISK_EXTCONFIG="/etc/asterisk/extconfig.conf"
ASTERISK_LDAP="/etc/asterisk/res_ldap.conf"
ASTERISK_MAIL="/etc/asterisk/voicemail.conf"

# configure Asterisk
sed -i "s/^;\?realm=.*/realm=$DOMAIN/" $ASTERISK_SIP
sed "s/^;\?allow=[[:alnum:]]\+\([[:space:]]\+; Allow codecs in order of preference\)$/allow=all\1/" -i $ASTERISK_SIP
sed -i 's/;rtcachefriends=yes/rtcachefriends=yes/' $ASTERISK_SIP
sed "s/^;\?language=[[:alnum:]]\+\([[:space:]]\+; Default language setting for all users\/peers\)$/language=$asterisk_lang\1/" -i $ASTERISK_SIP

if ! `grep -q 'Realtime/@' $ASTERISK_EXTENSIONS`; then
        echo '[internal]' >> $ASTERISK_EXTENSIONS
        echo 'switch => Realtime/@' >> $ASTERISK_EXTENSIONS
fi

if ! `grep -q sipusers $ASTERISK_EXTCONFIG`; then
        echo "sipusers => ldap,\"ou=people,$MDSSUFFIX\",sip" >> $ASTERISK_EXTCONFIG
fi

sed -i "s/;sippeers =.*/sippeers => ldap,\"ou=people,$MDSSUFFIX\",sip/" $ASTERISK_EXTCONFIG
sed -i "s/;extensions =.*/extensions => ldap,\"ou=extensions,ou=asterisk,$MDSSUFFIX\",extensions/" $ASTERISK_EXTCONFIG
sed -i "s/;voicemail =.*/voicemail => ldap,\"ou=voicemail,ou=asterisk,$MDSSUFFIX\",voicemail/" $ASTERISK_EXTCONFIG

sed -i 's/;host=192.168.1.1/host=127.0.0.1/' $ASTERISK_LDAP
sed -i 's/;protocol=3/protocol=3/' $ASTERISK_LDAP
sed -i "s/;basedn=dc=example,dc=tld/basedn=$MDSSUFFIX/" $ASTERISK_LDAP
sed -i "s/;user=cn=asterisk,dc=example,dc=tld/user=uid=LDAP Admin,ou=System Accounts,$MDSSUFFIX/" $ASTERISK_LDAP
sed -i "s/;pass=MyPassword/pass=$MDSPASS/" $ASTERISK_LDAP

sed -i 's/context  =  AstExtensionContext/context = AstContext/' $ASTERISK_LDAP
sed -i 's/exten  =  AstExtensionExten/exten = AstExtension/' $ASTERISK_LDAP
sed -i 's/priority = AstExtensionPriority/priority = AstPriority/' $ASTERISK_LDAP
sed -i 's/app = AstExtensionApplication/app = AstApplication/' $ASTERISK_LDAP
sed -i 's/appdata = AstExtensionApplicationData/appdata = AstApplicationData/' $ASTERISK_LDAP
sed -i 's/additionalFilter=(objectClass=AstExtension)/additionalFilter=(objectClass=AsteriskExtension)/' $ASTERISK_LDAP

sed 's!^;*\(name[[:space:]]*=[[:space:]]*\)[[:alnum:]]*\([[:space:]]*; We use the "cn" as the default value for name on the line above\)$!\1uid\2!' -i $ASTERISK_LDAP

cat << EOF >> $ASTERISK_LDAP
[voicemail]
context = AstVoicemailContext
mailbox = AstVoicemailMailbox
password = AstVoicemailPassword
fullname = AstVoicemailFullname
email = AstVoicemailEmail
pager = AstVoicemailPager
tz = AstVMTz
attach = AstVMAttach
saycid = AstVMSaycid
dialout = AstVMDialout
callback = AstVMCallback
review = AstVMReview
operator = AstVMOperator
envelope = AstVMEnvelope
sayduration = AstVMSayduration
saydurationm = AstVMSaydurationm
sendvoicemail = AstVMSendvoicemail
delete = AstVMDelete
nextaftercmd = AstVMNextastercmd
forcename = AstVMForcename
forcegreetings = AstVMForcegreetings
hidefromdir = AstVMHidefromdir
stamp = AstVMStamp
additionalFilter = (objectClass=AsteriskVoicemail)
EOF

sed -i 's/;\? searchcontexts=yes/searchcontexts=yes/' $ASTERISK_MAIL

restart_service asterisk

# configure the firewall
cat << EOF > /etc/shorewall/macro.SIP
#
# Shorewall version 4 - SIP Macro
#
# /usr/share/shorewall/macro.SIP
#
#	This macro handles SIP traffic.
#
###############################################################################
#ACTION SOURCE  DEST    PROTO   DEST    SOURCE  RATE    USER/
#                               PORT(S) PORT(S) LIMIT   GROUP
 PARAM  -	-	udp     5060
EOF

grep -q 'SIP' /etc/mmc/plugins/shorewall.ini || sed -i 's!,Whois!,Whois,SIP!' /etc/mmc/plugins/shorewall.ini

[ $fw_lan == "on" ] && mss-add-shorewall-rule -a SIP/ACCEPT -t lan
[ $fw_lan == "on" ] && mss-add-shorewall-rule -a SIP/ACCEPT -t wan

restart_service shorewall
restart_service mmc-agent

info_b $"The VoIP service is configured."
info $"You can add IP number to your users through the management interface at https://@HOSTNAME@/mmc/."
info $"Use @HOSTNAME@ as the server."
