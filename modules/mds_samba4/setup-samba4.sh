#!/bin/bash

. ../functions.sh
check_root
check_mmc_configured

python -u ./provision.py "$1" "$2" "$3" "$4" "$5" "$6" "$7"
if [ "$?" != "0" ]; then
    exit 1
else
    info "Samba4 has been provisioned successfully"
fi

# confirmation
info_b $"You can now use the management interface to manage your Windows users and shares at https://@HOSTNAME@/mmc/."

exit 0
