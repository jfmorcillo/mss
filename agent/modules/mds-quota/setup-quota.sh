#!/bin/bash

. ../functions.sh

userquota_tpl="templates/userquota.ini.tpl"

filesystems=$1

for fs in $filesystems; do
    tmp=$fs";"
done

# install template
backup /etc/mmc/plugins/userquota.ini
cat $userquota_tpl > /etc/mmc/plugins/userquota.ini
sed -i "s/\@FILESYSTEMS\@/$tmp/" /etc/mmc/plugins/userquota.ini

# add user quota option
# backup /etc/fstab

sleep 1
exit 0
