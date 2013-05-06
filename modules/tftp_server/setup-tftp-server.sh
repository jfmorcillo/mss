#!/bin/bash
# Copyright Mandriva 2013 all rights reserved

# INCLUDES
. '../functions.sh'

# CHECKS
check_mmc_configured

# PARAMETERS
fw_lan=$1
fw_wan=$2

# Configure TFTP server
mv -f /var/lib/tftpboot /var/lib/tftp
sed -i 's!-s /var/lib/tftpboot!-s --retransmit 5000000 /var/lib/tftp!' /etc/xinetd.d/tftp
sed -i 's!disable\(.*\)=\(.*\)yes!disable\1=\2no!' /etc/xinetd.d/tftp
restart_service xinetd

# Configure the Firewall
[ $fw_lan == "on" ] && mss-add-shorewall-rule -a TFTP/ACCEPT -t lan
[ $fw_wan == "on" ] && mss-add-shorewall-rule -a TFTP/ACCEPT -t wan
restart_service shorewall

info_b $"TFTP server is running."
info $"Your initial repository in located in '/var/lib/tftp'"

exit 0
