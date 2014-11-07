dev tun
server @NETWORK@
port 1194
proto udp

ca ca.crt
cert @HOSTNAME@.crt
key @HOSTNAME@.key
dh dh2048.pem

script-security 2
username-as-common-name

client-cert-not-required
# Allow client to see other clients
client-to-client

### LDAP AUTH ###
plugin /usr/lib64/openvpn/plugins/openvpn-auth-ldap.so "ldap-auth.config"

# @TODO If DNS is installed (echo "select modules from ... where name='mds_dns';" | sqlite3 /var/lib/mss/mss-agent.db), uncomment and replace @HOSTNAME@
#push dhcp-option DNS "@HOSTNAME@"
# @TODO Create a domain vpn.@DOMAIN@
#push dhcp-option DOMAIN "vpn.@DOMAIN@"

inactive 600
tcp-nodelay

keepalive 10 120
comp-lzo

persist-key
persist-tun

status onlineusers.log 5
status-version 1

verb 2
mute 10
reneg-sec 1800

# Avoid filling syslog with useless logs
mute-replay-warnings

