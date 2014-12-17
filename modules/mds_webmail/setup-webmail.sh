#!/bin/bash
# Copyright Mandriva 2009, 2010 all rights reserved

. '../functions.sh'

check_root

fw_lan=$1
fw_wan=$2

roundcube_db_conf_template="templates/db.inc.php.tpl"
roundcube_main_conf_template="templates/main.inc.php.tpl"
mbs_logo="templates/mbs_logo.png"

# copy the logo
cp -f $mbs_logo /usr/share/roundcubemail/skins/

# copy the db config
backup /etc/roundcubemail/db.inc.php
cat $roundcube_db_conf_template > /etc/roundcubemail/db.inc.php

# setup the roundcube db
if [ -f /var/lib/roundcubemail/sqlite.db ]; then
    rm -f /var/lib/roundcubemail/sqlite.db
fi
mkdir -p /var/lib/roundcubemail
chown apache /var/lib/roundcubemail
sqlite /var/lib/roundcubemail/sqlite.db < /usr/share/doc/roundcubemail/SQL/sqlite.initial.sql
chown apache:apache /var/lib/roundcubemail/sqlite.db
chmod 0600 /var/lib/roundcubemail/sqlite.db

# set correct permissions
chmod 770 /var/log/roundcubemail

# http -> https redirection
https_redirect roundcubemail /etc/httpd/conf/webapps.d/roundcubemail.conf

restart_service httpd

# copy main config
backup /etc/roundcubemail/main.inc.php
cat $roundcube_main_conf_template > /etc/roundcubemail/main.inc.php

# configure the Firewall
[ $fw_lan == "on" ] && mss-add-shorewall-rule -a Web/ACCEPT -t lan
[ $fw_wan == "on" ] && mss-add-shorewall-rule -a Web/ACCEPT -t wan
restart_service shorewall

info_b $"Webmail Roundcube is installed on your server."
info $"You can access the webmail interface at https://@HOSTNAME@/roundcubemail/."
