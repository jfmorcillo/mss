#!/bin/bash

set -e

. '../functions.sh'

check_root

LIBVIRTD_SYSCONFIG=templates/sysconfig-libvirtd
LIBVIRTD_CONF=templates/libvirtd.conf
QEMU_CONF=templates/qemu.conf
QEMU_SASL=templates/sasl2-qemu.conf
SHOREWALL_MACRO=templates/macro.Libvirtd
APACHE_CONF="templates/libvirt-apache.conf"

# set configuration
cp -f $LIBVIRTD_CONF /etc/libvirt/libvirtd.conf
cp -f $SHOREWALL_MACRO /etc/shorewall/macro.Libvirtd
cp -f $QEMU_CONF /etc/libvirt/qemu.conf
cp -f $QEMU_SASL /etc/sasl2/qemu.conf
cp -f $LIBVIRTD_SYSCONFIG /etc/sysconfig/libvirtd

# start service
restart_service libvirtd

# define password for admin
admin_password=$1
echo $admin_password | saslpasswd2 -p -a libvirt admin

sleep 2

# Pool setup
pool_location=$2
mkdir -p $pool_location
virsh pool-destroy default 2>/dev/null || echo "No default pool found."
virsh pool-undefine default 2>/dev/null || echo ""
virsh pool-define-as --type dir --name default --target $pool_location
virsh pool-autostart default
virsh pool-start default

restart_service libvirtd

# Install documentation
cp $APACHE_CONF /etc/httpd/conf/webapps.d/libvirt.conf
restart_service httpd

shift 2

function configure_bridge {
    CONFIG_DIR=/etc/sysconfig/network-scripts
    interface_conf=${CONFIG_DIR}/ifcfg-${1}
    if [ -f $interface_conf ]; then
        echo -n "Configuring bridge on interface $1..."
        bridge_name=br${1: -1}
        bridge_conf=${CONFIG_DIR}/ifcfg-${bridge_name}

        cp -f $interface_conf $bridge_conf
        sed -i "s/^DEVICE=.*/DEVICE=$bridge_name/" $bridge_conf
        echo "TYPE=Bridge" >> $bridge_conf
        echo "BRIDGE=${bridge_name}" >> $interface_conf
        echo "done."

        echo -n "Configuring bridge firewall."
        sed -i "s/$1/$bridge_name/" /etc/shorewall/interfaces
        echo "done."
    fi
}

while [ $# -ne 0 ]; do
    if [[ $1 == eth* ]] || [[ $1 == en* ]]; then
        [ "$2" == "on" ] && configure_bridge $1 && restart_service network
    else
        # shorewall configuration
        [ $1 == "on" ] && mss-add-shorewall-rule -a Libvirtd/ACCEPT -t lan
        [ $2 == "on" ] && mss-add-shorewall-rule -a Libvirtd/ACCEPT -t wan
        restart_service shorewall
    fi
    shift 2
done

info_b $"Libvirt and KVM are now installed and configured."
info $"Login to libvirt with the virt-manager client using TCP/SASL method:"
info $"- Hostname is @HOSTNAME@"
info $"- Username is admin"
info $"- Password is $admin_password"
