mode server
tls-server
port 1194
proto udp
dev tun

topology subnet

ca ca.crt
cert @HOSTNAME@.crt
key  @HOSTNAME@.key
dh   dh2048.pem

script-security 2
username-as-common-name

client-cert-not-required
# Allow client to see other clients
client-to-client

### LDAP AUTH ###
plugin /usr/lib64/openvpn/plugins/openvpn-auth-ldap.so "ldap-auth.config"
#################

# @TODO Change the netmask to be correct according to @SERVER@
server @SERVER@ 255.255.255.0
# @TODO ask the net and mask to the user
# push "route 10.0.0.0 255.0.0.0"

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
ifconfig-pool-persist fixip.txt 0

verb 3
mute 10
reneg-sec 1800
