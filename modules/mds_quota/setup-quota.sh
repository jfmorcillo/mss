#!/bin/bash

. ../functions.sh

check_mmc_configured

userquota_tpl="templates/userquota.ini.tpl"

fss=$1

add_schema templates/quota.schema

backup /etc/fstab
for f in $fss; do
    # get UUID
    dev=`echo $f | cut -d: -f1`
    uuid=`blkid | grep $dev | sed 's/.*PARTUUID="\([a-f0-9-]*\)".*$/\1/'`
    # add usrquota option
    mountpoint=`grep PARTUUID=${uuid} /etc/fstab | sed "s/^PARTUUID=${uuid}[[:space:]]\+\([^[:space:]]\+\).*$/\1/"`
    fs=`grep PARTUUID=${uuid} /etc/fstab | sed "s/^PARTUUID=${uuid}[[:space:]]\+[^[:space:]]\+[[:space:]]\+\([^[:space:]]\+\).*$/\1/"`
    grep $uuid /etc/fstab | grep -q usrquota
    if [ $? -ne 0 ]; then
        echo "Add usrquota option for $mountpoint"
        sed -i "s/^\(PARTUUID=${uuid}[[:space:]]\+[^[:space:]]\+[[:space:]]\+[^[:space:]]\+[[:space:]]\+\)\([^[:space:]]\+\)\(.*\)$/\1\2,usrquota\3/" /etc/fstab
        if [ "$fs" == "ext3" ] || [ "$fs" == "ext4" ]; then
            echo "Remount $mountpoint"
            mount -o remount,usrquota $mountpoint
            echo "Create quota files for $mountpoint"
            quotacheck -cum $mountpoint
            quotaon -u $mountpoint
            echo "Quotas activated on $mountpoint"
        elif [ "$fs" == "xfs" ]; then
            echo "Quotas configured on $mountpoint"
            echo "Restart the system to activate quotas"
        else
            error $"Quotas not supported on this filesystem : $fs"
            exit 1
        fi
    else
        echo "Quota option already present for $mountpoint"
    fi
    tmp=`echo $f | sed "s/:/:1024:/"`
    filesystems=${filesystems}${tmp}","
done

# install template
backup /etc/mmc/plugins/userquota.ini
cat $userquota_tpl > /etc/mmc/plugins/userquota.ini
sed -i "s!\@FILESYSTEMS\@!${filesystems%?}!" /etc/mmc/plugins/userquota.ini

restart_service slapd
restart_service mmc-agent /var/log/mmc/mmc-agent.log

info_b $"Quota module is activated in the management interface."
info $"You can now configure user quotas from the management interface : https://@HOSTNAME@/mmc/."

exit 0
