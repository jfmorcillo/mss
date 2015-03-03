#!/bin/bash

. ../functions.sh

check_root

function build_net_conf() {
    conf=`mktemp`
    echo DEVICE=$1 > $conf
    if [ $2 = static ]; then
        echo ONBOOT=yes >> $conf
        echo BOOTPROTO=none >> $conf
        echo IPADDR=$3 >> $conf
        echo NETMASK=$4 >> $conf
        [[ ! $5x = x ]] && echo DNS1=$5 >> $conf
        [[ ! $6x = x ]] && echo DNS2=$6 >> $conf
        [[ ! $7x = x ]] && echo DOMAIN=$7 >> $conf
        [[ ! $8x = x ]] && echo GATEWAY=$8 >> $conf
    elif [ $2 = dhcp ]; then
        echo ONBOOT=yes >> $conf
        echo BOOTPROTO=dhcp >> $conf
    else
        echo ONBOOT=no >> $conf
        echo BOOTPROTO=none >> $conf
    fi
    # Write the conf
    mv $conf /etc/sysconfig/network-scripts/ifcfg-$1
}

function begin_shorewall_conf() {
    shorewall_interfaces=`mktemp`
    shorewall_zones=`mktemp`
    shorewall_policy=`mktemp`
    shorewall_rules=`mktemp`
    echo fw     all     ACCEPT >> $shorewall_policy
    echo fw     firewall >> $shorewall_zones
    echo SECTION NEW >> $shorewall_rules
}

function build_shorewall_conf() {
    echo $2 $1 detect >> $shorewall_interfaces
    echo $2 ipv4 >> $shorewall_zones
    echo $2     fw      DROP >> $shorewall_policy
}

function end_shorewall_conf() {
    # Finish shorewall conf
    for lan_zone in $lan_zones
    do
        for wan_zone in $wan_zones
        do
            echo $lan_zone  $wan_zone   ACCEPT >> $shorewall_policy
            echo $wan_zone  $lan_zone   DROP >> $shorewall_policy
        done
    done
    echo all all DROP >> $shorewall_policy
    # write conf
    backup /etc/shorewall/zones
    backup /etc/shorewall/interfaces
    backup /etc/shorewall/policy
    old_rules=`mybackup /etc/shorewall/rules`
    mv $shorewall_zones /etc/shorewall/zones
    mv $shorewall_interfaces /etc/shorewall/interfaces
    mv $shorewall_policy /etc/shorewall/policy
    mv $shorewall_rules /etc/shorewall/rules
}

function allow() {
    service=$1
    zones=$2
    for zone in $zones
    do
        [ $service = mss ] && echo ACCEPT         $zone  fw  tcp     8000 >> $shorewall_rules
        [ $service = ssh ] && echo SSH/ACCEPT     $zone  fw >> $shorewall_rules
        echo Ping/ACCEPT     $zone  fw >> $shorewall_rules
    done
}

lan_zones=""
wan_zones=""
old_rules=""

begin_shorewall_conf

while [ $# -ne 0 ]; do
    if [[ $1 = eth* ]] || [[ $1 = br* ]] || [[ $1 = en* ]]; then
        [[ $2 = lan* ]] && lan_zones="$lan_zones $2"
        [[ $2 = wan* ]] && wan_zones="$wan_zones $2"
        build_net_conf "$1" "$3" "$4" "$5" "$6" "$7" "$8" "$9" && \
        [ ! "$2" = "none" ] && build_shorewall_conf "$1" "$2"
        shift 9
    else
        # MSS/SSH firewall
        # internal
        if [ -n "$lan_zones" ]; then
            [ $1 = "on" ] && allow mss "$lan_zones"
            [ $2 = "on" ] && allow ssh "$lan_zones"
        fi
        # external
        if [ -n "$wan_zones" ]; then
            [ $3 = "on" ] && allow mss "$wan_zones"
            [ $4 = "on" ] && allow ssh "$wan_zones"
        fi
        shift 4
    fi
done

end_shorewall_conf

python backport_old_rules "$old_rules"

info_b $"Network and firewall configured."

exit 0
