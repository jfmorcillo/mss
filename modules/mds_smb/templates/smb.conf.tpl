[global]
workgroup = @WORKGROUP@
netbios name = @NETBIOSNAME@
server string = Mandriva Directory Server - SAMBA %v
null passwords = yes
name resolve order = bcast host
domain logons = yes
domain master = yes

time server = yes
wins support = yes

printing = cups
printcap name = cups

# profiles #
# logon path = \\%N\profiles\%U
logon path =
logon script = logon.bat

map acl inherit = yes
inherit acls = yes
inherit permissions = yes
nt acl support = yes
force unknown acl user = yes

passdb backend = ldapsam:ldap://127.0.0.1/
ldap admin dn = uid=LDAP Admin,ou=System Accounts,@SUFFIX@
ldap suffix = @SUFFIX@
ldap group suffix = ou=Group
ldap user suffix = ou=People
ldap machine suffix = ou=Hosts
ldap idmap suffix = ou=Idmap
ldap passwd sync = yes
idmap backend = ldap:ldap://127.0.0.1/
idmap uid = 20000-30000
idmap gid = 20000-30000

enable privileges = yes
add machine script = /usr/lib/mmc/add_machine_script '%u'
add share command = /usr/lib/mmc/add_change_share_script
delete share command = /usr/lib/mmc/delete_share_script
add printer command = /usr/lib/mmc/add_printer_script
deleteprinter command = /usr/lib/mmc/delete_printer_script

[homes]
comment = Home directories
browseable = no
writeable = yes
create mask = 0700
directory mask = 0700

[public]
comment = Public share
path = /home/samba/shares/public
browseable = yes
public = yes
writeable = yes

[archives]
comment = Backup share
path = /home/archives
browseable = yes
public = no
writeable = no

[printers]
comment = All printers
path = /var/spool/samba
public = yes
guest ok = yes
browseable = no
writeable = no
printable = yes

[print$]
comment = Printer Driver Download Area
path = /var/lib/samba/printers
browseable = no
guest ok = yes
read only = yes
write list = +"Print Operators"
force group = "Print Operators"
create mask = 0775
directory mask = 0775

[netlogon]
comment = Network Logon Service
path = /home/samba/netlogon
guest ok = yes
browseable = no
writable = yes

# profiles #
# [profiles]
# path = /home/samba/profiles
# writeable = yes
# create mask = 0700
# directory mask = 0700
# browseable = no


