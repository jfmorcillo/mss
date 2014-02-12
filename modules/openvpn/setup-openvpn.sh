#!/bin/bash
# Copyright Mandriva 2013 all rights reserved

# INCLUDES
. '../functions.sh'

# BASIC VERIFICATIONS
check_mmc_configured

# PARAMETERS
country=$1
province=$2
city=$3
org=$4
email=$5
network=$6
iface_name=`echo $7 | cut -d ' ' -f1`
iface_addr=`echo $7 | cut -d ' ' -f2`

# DEFINES
OPENVPN_AUTHCONF="templates/ldap-auth.config.tpl"
OPENVPN_SERVERFILE="templates/vpnserver-ldap-auth.conf.tpl"
OPENVPN_VARS="templates/vars.tpl"
CLIENT_CONF_TPL="templates/mbs_vpn_client.ovpn.tpl"
APACHE_CONF="templates/openvpn-apache.conf"
SERVICE="templates/openvpn-vpnserver-ldap-auth.service"

EASYRSA_PATH=`mktemp -d`
cp -r /usr/share/openvpn/easy-rsa/* ${EASYRSA_PATH}

# TEMPLATE INSTANCES
# Copy config file at the good location
cp -f $OPENVPN_AUTHCONF /etc/openvpn/ldap-auth.config
cp -f $OPENVPN_SERVERFILE /etc/openvpn/vpnserver-ldap-auth.conf
cp -f $OPENVPN_VARS $EASYRSA_PATH/vars

sed -i "s!\@COUNTRY\@!$country!" $EASYRSA_PATH/vars
sed -i "s!\@PROVINCE\@!$province!" $EASYRSA_PATH/vars
sed -i "s!\@CITY\@!$city!" $EASYRSA_PATH/vars
sed -i "s!\@ORG\@!$org!" $EASYRSA_PATH/vars
sed -i "s!\@EMAIL\@!$email!" $EASYRSA_PATH/vars
sed -i "s!\@HOSTNAME\@!$HOST!" $EASYRSA_PATH/vars

sed -i "s!\@MDSSUFFIX\@!$MDSSUFFIX!" /etc/openvpn/ldap-auth.config

sed -i "s!\@HOSTNAME\@!$HOST!" /etc/openvpn/vpnserver-ldap-auth.conf
sed -i "s!\@SERVER\@!$network!" /etc/openvpn/vpnserver-ldap-auth.conf
# Create keys

#TODO: Change  "export KEY_CN=changeme"
pushd $EASYRSA_PATH
    source ./vars
    #make sure all is clean and OK.
    ./clean-all
    ./build-dh
    ./pkitool --initca
    ./pkitool --server $HOSTNAME
    mv ./keys/*.{crt,key} ./keys/dh2048.pem /etc/openvpn
popd
rm -rf ${EASYRSA_PATH}

# Create mmc group
python templates/mmc_groupadd.py -g VPNUsers -d "Users authorized to gain access to VPN"

# Install documentation
cp $APACHE_CONF /etc/httpd/conf/webapps.d/openvpn.conf

# Build configuration
[ -d configuration ] && rm -rf configuration
mkdir configuration
CLIENT_CONF=configuration/vpn_${HOSTNAME}.ovpn
cp $CLIENT_CONF_TPL $CLIENT_CONF
sed -i -re 's/@REMOTE@/'"$iface_addr 1194"'/' $CLIENT_CONF
pushd configuration
    cp /etc/openvpn/ca.crt .
    zip vpn_config_client *
    rm ca.crt vpn_${HOSTNAME}.ovpn
popd

restart_service httpd

cp $SERVICE /etc/systemd/system
systemctl daemon-reload
enable_service openvpn-vpnserver-ldap-auth
restart_service openvpn-vpnserver-ldap-auth

# Shorewall configuration
mss-add-shorewall-rule -a ACCEPT -t $iface_name -p udp -P 1194
vpn_dev=`ip route get $network | head -n1 | awk '{ print $4; }'`
vpn_ip=`ip route get $network | head -n1 | awk '{ print $NF; }'`
vpn_zone=`echo $vpn_dev | sed 's/tun/vpn/'`
grep -q $vpn_zone /etc/shorewall/policy
if [ $? -ne 0 ]; then
    echo "$vpn_zone $vpn_dev detect routeback" >> /etc/shorewall/interfaces
    echo "$vpn_zone ipv4" >> /etc/shorewall/zones
    sed -i "s/^all all DROP/$vpn_zone fw ACCEPT\nall all DROP/" /etc/shorewall/policy
fi
restart_service shorewall

info_b $"The VPN service is running."
info $"- The VPN network address is $network"
info $"- The server IP in the VPN network is $vpn_ip"
info $"- Documentation for this addon is available at http://@HOSTNAME@/openvpn-documentation/"
info $"- An archive containing the clients configuration files is available in the addon's menu. Use it to configure your clients."
