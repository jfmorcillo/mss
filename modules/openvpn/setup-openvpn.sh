#!/bin/bash
#
# (c) 2012-2014 Mandriva, http://www.mandriva.com/
#
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

set -e

# INCLUDES
. '../functions.sh'

# BASIC VERIFICATIONS
check_mmc_configured

# PARAMETERS

# gets an array of (IP, zone)
listen=(${1//:/ })
network=$2
push_networks=$3

country=$4
province=$5
city=$6
org=$7
email=$8

# DEFINES
ZONE_NAME="vpn"
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

# OpenVPN configuration
sed -i "s!\@HOSTNAME\@!$HOST!" /etc/openvpn/vpnserver-ldap-auth.conf
sed -i "s!\@NETWORK\@!${network//\// }!" /etc/openvpn/vpnserver-ldap-auth.conf

# Setup routes
for push_network in $push_networks
do
    echo push \"route ${push_network//\// }\" >> /etc/openvpn/vpnserver-ldap-auth.conf
done

# Create keys

#TODO: Change  "export KEY_CN=changeme"
pushd $EASYRSA_PATH
    source ./vars
    # make sure all is clean and OK.
    ./clean-all
    ./build-dh
    ./pkitool --initca
    ./pkitool --server $HOSTNAME
    mv ./keys/*.{crt,key} ./keys/dh2048.pem /etc/openvpn
popd
rm -rf ${EASYRSA_PATH}

# Create mmc group
python mmc_groupadd.py -d $"Users authorized to connect to the VPN" VPNUsers

# Install documentation
cp $APACHE_CONF /etc/httpd/conf/webapps.d/openvpn.conf

# Build client configuration
[ -d configuration ] && rm -rf configuration
mkdir configuration
CLIENT_CONF=configuration/vpn_${HOSTNAME}.ovpn
cp $CLIENT_CONF_TPL $CLIENT_CONF
sed -i -re 's/@REMOTE@/'"${listen[0]} 1194"'/' $CLIENT_CONF
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

## Shorewall configuration
vpn_dev=`ip route get $network | head -n1 | awk '{ print $4; }'`
vpn_ip=`ip route get $network | head -n1 | awk '{ print $NF; }'`

if ! grep -q $ZONE_NAME /etc/shorewall/policy
then
  backup /etc/shorewall/policy
  backup /etc/shorewall/interfaces
  backup /etc/shorewall/zones
  backup /etc/shorewall/rules
  echo "$ZONE_NAME $vpn_dev detect routeback" >> /etc/shorewall/interfaces
  echo "$ZONE_NAME ipv4" >> /etc/shorewall/zones
  # setup policies and rules
  python setup-fw.py
fi

cp -f templates/macro.OpenVPN /etc/shorewall
mss-add-shorewall-rule -a OpenVPN/ACCEPT -t ${listen[1]}
restart_service shorewall

# Add the vpn zone to the shorewall module configuration
MMC_SHOREWALL=/etc/mmc/plugins/shorewall.ini
if ! grep -q "internal_zones_names" $MMC_SHOREWALL | grep -q $ZONE_NAME
then
  sed -i "s|internal_zones_names\s*=\s*\(.*\)$|internal_zones_names = \1 $ZONE_NAME|" $MMC_SHOREWALL
  restart_service mmc-agent
fi

info_b $"The VPN service is running."
info $"- The VPN network address is $network"
info $"- The server IP in the VPN network is $vpn_ip"
info $"- Documentation for this addon is available at http://@HOSTNAME@/openvpn-documentation/"
info $"- An archive containing the clients configuration files is available in the addon's menu. Use it to configure your clients."
