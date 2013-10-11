#!/bin/bash
# Copyright Mandriva 2013 all rights reserved

# INCLUDES
. '../functions.sh'

# CHECKS
check_mmc_configured

dhcp_configured=""
dhcp_external=""

function configure_firewall() {
    echo "Firewall configuration..."
    if_name=$1
    if_zone=$2
    if_zone_type=`echo $if_zone | sed 's![0-9]*!!g'`
    # Firewall configuration
    cp -f macro.Pulse2Imaging /etc/shorewall
    mss-add-shorewall-rule -a Pulse2Imaging/ACCEPT -t $if_zone_type
    restart_service shorewall
}

function configure_imaging() {
    echo "Configuring the package server for imaging"
    package_srv_conf=/etc/mmc/pulse2/package-server/package-server.ini
    uuid=`uuidgen`
    sed -i 's!^# mount_point!mount_point!' $package_srv_conf
    sed -i "s!^# uuid =.*!uuid = ${uuid}!" $package_srv_conf
    enable_service pulse2-package-server
    service pulse2-package-server stop
    restart_service pulse2-package-server

    # Enable the imaging plugin
    sed -i 's!^disable.*$!disable = 0!' /etc/mmc/plugins/imaging.ini
    restart_service mmc-agent

    echo "Registering the imaging server"
    mmc_agent_conf=/etc/mmc/agent/config.ini
    mmc_login=`grep '^login' $mmc_agent_conf | sed 's/^.*[[:space:]]\+=[[:space:]]\+//'`
    mmc_password=`grep '^password' $mmc_agent_conf | sed 's/^.*[[:space:]]\+=[[:space:]]\+//'`
    mmc_host=`grep '^host' $mmc_agent_conf | sed 's/^.*[[:space:]]\+=[[:space:]]\+//'`
    mmc_port=`grep '^port' $mmc_agent_conf | sed 's/^.*[[:space:]]\+=[[:space:]]\+//'`
    pulse2-package-server-register-imaging -m https://$mmc_login:$mmc_password@$mmc_host:$mmc_port --check
    if [ $? -eq 0 ]; then
        pulse2-package-server-register-imaging -m https://$mmc_login:$mmc_password@$mmc_host:$mmc_port --name "MBS imaging server"
        [ $? -ne 0 ] && error $"Failed to register the imaging server" && exit 1
    fi

    echo "Associating the imaging server and creating a default boot menu"
    pulse2-load-defaults --default-menu --link-server

    echo "Configuring directories..."
    # Create missing directories
    if [ ! -d /var/lib/pulse2/imaging/bootmenus ]; then
        mkdir /var/lib/pulse2/imaging/bootmenus
    fi
    if [ ! -d /var/lib/pulse2/imaging/isos ]; then
        mkdir /var/lib/pulse2/imaging/isos
    fi

    # Set permissions
    python add_group.py
    chgrp -R Pulse-Admins /var/lib/pulse2/imaging/postinst /var/lib/pulse2/imaging/isos
    chmod -R g+w /var/lib/pulse2/imaging/postinst /var/lib/pulse2/imaging/isos

    # Configure TFTP server
    echo "Configuring TFTP repository..."
    if [ ! -d /var/lib/tftp/imaging ]; then
        mkdir -p /var/lib/tftp/imaging
    fi
    # Tune fstab if needed
    grep -q 'tftp/imaging' /etc/fstab
    if [ $? -eq 1 ]; then
        echo '' >> /etc/fstab
        echo '# Pulse2 tftp entry' >> /etc/fstab
        echo '/var/lib/pulse2/imaging	/var/lib/tftp/imaging	none	auto,bind	0 0' >> /etc/fstab
        mount /var/lib/tftp/imaging
    fi

    # Configure NFS share
    echo "Configuring NFS shares..."
    if [ ! -f /etc/exports ]; then
        touch /etc/exports
    fi
    grep -q "pulse2_imaging: configured" /etc/exports
    if [ $? -eq 1 ]; then
        echo "" >> /etc/exports
        echo "# Pulse2 Imaging Exports" >> /etc/exports
        echo "/var/lib/pulse2/imaging/computers 0.0.0.0/0.0.0.0(async,rw,no_root_squash,subtree_check)" >> /etc/exports
        echo "/var/lib/pulse2/imaging/masters 0.0.0.0/0.0.0.0(async,rw,no_root_squash,subtree_check)" >> /etc/exports
        echo "/var/lib/pulse2/imaging/postinst 0.0.0.0/0.0.0.0(async,ro,no_root_squash,subtree_check)" >> /etc/exports
        echo "# pulse2_imaging: configured" >> /etc/exports
        echo "" >> /etc/exports
        restart_service nfs-common
    fi

    # Configure Samba shares if samba is installed
    if [ -f /etc/samba/smb.conf ] && [ -f /usr/sbin/samba ]; then
        echo "Configuring Samba shares..."
        grep -q "pulse2_imaging: configured" /etc/samba/smb.conf
        if [ $? -eq 1 ]; then
            echo "" >> /etc/samba/smb.conf
            echo "[iso]" >> /etc/samba/smb.conf
            echo "  comment = Pulse2 ISO images" >> /etc/samba/smb.conf
            echo "  path = /var/lib/pulse2/imaging/isos" >> /etc/samba/smb.conf
            echo "  browseable = yes" >> /etc/samba/smb.conf
            echo "  writable = yes" >> /etc/samba/smb.conf
            echo "  valid users = @Pulse-Admin" >> /etc/samba/smb.conf
            echo "" >> /etc/samba/smb.conf
            echo "[postinst]" >> /etc/samba/smb.conf
            echo "  comment = Pulse2 Postinstallation files" >> /etc/samba/smb.conf
            echo "  path = /var/lib/pulse2/imaging/postinst" >> /etc/samba/smb.conf
            echo "  browseable = yes" >> /etc/samba/smb.conf
            echo "  writable = yes" >> /etc/samba/smb.conf
            echo "  valid users = @Pulse-Admin" >> /etc/samba/smb.conf
            echo "# pulse2_imaging: configured" >> /etc/samba/smb.conf
            echo "" >> /etc/samba/smb.conf
            restart_service smb
        fi
    fi

    enable_service pulse2-imaging-server
    service pulse2-imaging-server stop
    restart_service pulse2-imaging-server
}

function configure_dhcp() {
    if_name=$1
    if_addr=$2
    if_netmask=$3
    echo "DHCP subnet creation configuration..."
    # create the DHCP subnet
    python mmc_dhcp.py -i $if_name -a $if_addr -n $if_netmask
    dhcp_configured="$dhcp_configured $if_name"
}

configure_imaging
while [ $# -ne 0 ]; do
    if [[ $1 = eth* ]]; then
        configure_firewall $1 $2
        [ $3 == "on" ] && configure_dhcp $1 $4 $5 || dhcp_external="$dhcp_external $1"
        shift 5
    fi
done

info_b $"Pulse2 imaging module is installed and configured."
info $"The module is available on the management interface at https://@HOSTNAME@/mmc/."
for interface in $dhcp_configured
do
    info $"- DHCP subnet configured on $interface for Pulse2 imaging clients."
done
for interface in $dhcp_external
do
    info $"- The external DHCP server used on $interface must be configured for Pulse2."
done
info $"Check the documentation to use the Pulse2 imaging at http://serviceplace.mandriva.com/addons/mbs/1.0/pulse2_imaging/."
