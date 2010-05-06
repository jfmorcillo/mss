[main]
disable = 0
# Computers Locations
baseComputersDN = ou=Hosts, @SUFFIX@
sambaConfFile = /etc/samba/smb.conf
sambaInitScript = /etc/rc.d/init.d/smb
sambaClamavSo = /usr/lib/samba/vfs/vscan-clamav.so
# Default SAMBA shares location
defaultSharesPath = /home/samba/shares
# You can specify authorized paths for share creation
# Default value is the defaultSharesPath value
# authorizedSharePaths = /shares, /opt, /srv

# Default value when adding samba attributes to an user
# DELETE means the attibute is removed from the user LDAP entry
[userDefault]
sambaPwdMustChange = DELETE
