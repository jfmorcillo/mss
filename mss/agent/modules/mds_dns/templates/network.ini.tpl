[main]
disable = 0

[dhcp]
enable = @DHCPENABLE@
dn = ou=DHCP,@SUFFIX@
pidfile = /var/run/dhcpd/dhcpd.pid
init = /etc/rc.d/init.d/dhcpd
logfile = /var/log/messages
leases = /var/lib/dhcp/dhcpd.leases
hostname = @HOSTNAME@

[dns]
enable = 1
dn = ou=DNS,@SUFFIX@
pidfile = /var/lib/named/var/run/named.pid
init = /etc/rc.d/init.d/named-sdb
logfile = /var/log/messages
bindroot = /var/named
bindgroup = named
# dnsreader = DNS Reader
# dnsreaderpassword = DNSReaderPassword
