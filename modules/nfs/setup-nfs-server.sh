#!/bin/bash
# Copyright Mandriva S/A all rights reserved
# This file is part of Mandriva Server Setup
#
# MSS is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MSS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MSS; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

# INCLUDES
. '../functions.sh'

# CHECKS
check_mmc_configured

# PARAMETERS
fw_lan=$1
fw_wan=$2

# configure NFS services for firewall
# /etc/sysconfig/nfs-common
sed -i 's!^STATD_OPTIONS=.*$!STATD_OPTIONS="--port 32765 --outgoing-port 32766"!' /etc/sysconfig/nfs-common
sed -i 's!^LOCKD_TCPPORT=.*$!LOCKD_TCPPORT=32678!' /etc/sysconfig/nfs-common
sed -i 's!^LOCKD_UDPPORT=.*$!LOCKD_UDPPORT=32679!' /etc/sysconfig/nfs-common
# /etc/sysconfig/nfs-server
sed -i 's!^RPCMOUNTD_OPTIONS=.*$!RPCMOUNTD_OPTIONS="--port 32767"!' /etc/sysconfig/nfs-server
sed -i 's!^RPCRQUOTAD_OPTIONS=.*$!RPCRQUOTAD_OPTIONS="-p 32769"!' /etc/sysconfig/nfs-server
# /etc/modprobe.d/99_nfs.conf
echo "# /etc/modprobe.d/99_nfs.conf" > /etc/modprobe.d/99_nfs.conf
echo "options nfs callback_tcpport=32764" >> /etc/modprobe.d/99_nfs.conf
echo "options lockd nlm_udpport=32768 nlm_tcpport=32768" >> /etc/modprobe.d/99_nfs.conf

# Restart NFS service
restart_service nfs-common
restart_service nfs-server
restart_service rpcbind

# Configure the Firewall
if [ ! -f /etc/shorewall/macro.NFS ]; then
    echo<<EOF > /etc/shorewall/macro.NFS
#
# Shorewall version 3.2 - NFS Macro
#
# /etc/shorewall/macro.NFS
#
#	This macro handles Network File Server (NFS)
#	Because NFS lacks all security you should not enable it over
#	Internet.
#       This macro is specific to MBS1 NFS installation
#
###############################################################################
#ACTION	SOURCE	DEST	PROTO	DEST	SOURCE	RATE	USER/
#				PORT(S)	PORT(S)	LIMIT	GROUP
PARAM	-	-	udp	111
PARAM	-	-	tcp	111
PARAM	-	-	udp	2049
PARAM	-	-	tcp	2049
PARAM	-	-	udp	32764:32769
PARAM	-	-	tcp	32764:32769

EOF
fi

# Internal interface
[ $fw_lan == "on" ] && mss-add-shorewall-rule -a NFS/ACCEPT -t lan

# External interface
[ $fw_wan == "on" ] && mss-add-shorewall-rule -a NFS/ACCEPT -t wan

restart_service shorewall

# Information
info_b $"The NFS service is running."
info_b $"Edit '/etc/exports' to add your NFS shares"

exit 0
