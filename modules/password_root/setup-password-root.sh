#!/bin/bash
# Copyright Mandriva 2013 all rights reserved

. '../functions.sh'

check_mmc_configured

old_password=`escape_sed $1`
new_password=`escape_sed $2`

result=`python check_root_password.py $old_password`
if [ $result -eq 0 ]; then
    echo root:$new_password | /usr/sbin/chpasswd && (info_b $"The password has been changed."; exit 0) || (error $"Failed to change the password."; exit 1)
else
    error $"Current password is not correct."
    exit 1
fi
