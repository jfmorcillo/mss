#!/bin/bash

. ../functions.sh

check_root

function build_net_conf() {
    conf=`mktemp`
    echo DEVICE=$1 > $conf
    echo ONBOOT=yes >> $conf
    if [ $2 = "static" ]; then
        echo BOOTPROTO=none >> $conf
        echo IPADDR=$3 >> $conf
        echo NETMASK=$4 >> $conf
        [[ ! $5x = x ]] && echo DNS1=$5 >> $conf
        [[ ! $6x = x ]] && echo DNS2=$6 >> $conf
        [[ ! $7x = x ]] && echo DOMAIN=$7 >> $conf
        [[ ! $8x = x ]] && echo GATEWAY=$8 >> $conf
    else
        echo BOOTPROTO=dhcp >> $conf
    fi
    # Disable ifplugd
    echo MII_NOT_SUPPORTED=yes >> $conf
    # Write the conf
    backup /etc/sysconfig/network-scripts/ifcfg-$1
    mv $conf /etc/sysconfig/network-scripts/ifcfg-$1
}

function begin_shorewall_conf() {
    shorewall_interfaces=`mktemp`
    shorewall_zones=`mktemp`
    shorewall_policy=`mktemp`
    echo fw     all     ACCEPT >> $shorewall_policy
}

function build_shorewall_conf() {
    echo $2 $1 detect >> $shorewall_interfaces
    echo $2 ipv4 >> $shorewall_zones
    [[ $2 = lan* ]] && echo $2 fw ACCEPT >> $shorewall_policy
    echo $2 all DROP info >> $shorewall_policy
}

function end_shorewall_conf() {
    # Finish shorewall conf
    echo fw firewall >> $shorewall_zones
    # Default policy
    echo all all DROP >> $shorewall_policy
    # write conf
    backup /etc/shorewall/zones
    backup /etc/shorewall/interfaces
    backup /etc/shorewall/policy
    mv $shorewall_zones /etc/shorewall/zones
    mv $shorewall_interfaces /etc/shorewall/interfaces
    mv $shorewall_policy /etc/shorewall/policy
}

begin_shorewall_conf

while [ $# -ne 0 ]; do
    [[ $1 = eth* ]] && build_net_conf "$1" "$3" "$4" "$5" "$6" "$7" "$8" "$9" && \
                       build_shorewall_conf "$1" "$2"
    shift 9
done

end_shorewall_conf

restart_service shorewall

echo 8Network is configured.
echo 8Restart the network service through the management interface to apply the configuration.
