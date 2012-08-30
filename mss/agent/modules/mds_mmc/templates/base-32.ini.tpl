[ldap]
# LDAP we are connected to
host = 127.0.0.1
# LDAP base DN
baseDN = @SUFFIX@
# Users location in the LDAP
baseUsersDN = ou=People, @SUFFIX@
# Groups location in the LDAP
baseGroupsDN = ou=Group, @SUFFIX@
# LDAP manager
rootName = uid=LDAP Admin,ou=System Accounts,@SUFFIX@
password = @PASSWORD@
# If enabled, the MMC will create/move/delete the home of the users
# Else will do nothing, but only write user informations into LDAP
userHomeAction = 1
# Skeleton directory to populate a new home directory
skelDir = /etc/skel
# If set, all new users will belong to this group when created
defaultUserGroup = users
# Default home directory for users
defaultHomeDir = /home
# user uid number start
uidStart = 10000
# group gid number start
gidStart = 10000
# LDAP log file path
logfile = /var/log/ldap/ldap.log
# FDS log file path
# logfile = /opt/fedora-ds/slapd-hostname/logs/access 
passwordscheme = passmod
# you can specify here where you can authorized creation of your homedir
# default is your defaultHomeDir
# example:
# authorizedHomeDir = /home, /home2, /mnt/depot/newhome

[backup-tools]
# Path of the backup tools
path = /usr/lib/mmc/backup-tools
# Where are put the archives
destpath = /home/archives

# User authentication configuration
#[authentication]
# Authenticators chain
#method = baseldap externalldap

# baseldap authenticator configuration
#[authentication_baseldap]
# Set a list of login that will only be authentified using this authenticator
#authonly = root

# Externalldap authenticator configuration
#[authentication_externalldap]
# Login list that won't be authenticated with this authenticator
#exclude = root
# LDAP server URL
#ldapurl = ldap://192.168.0.1:389
# LDAP suffix where to search for user
#suffix = cn=Users,dc=edge-it,dc=subnet
# How to bind to the LDAP. Empty if anonymous
#bindname = cn=account, cn=Users, dc=linboxad, dc=subnet
#bindpasswd = s3cr3t
#bindname =
#bindpasswd =
# User filter
#filter = objectClass=*
# User attribute containing her/his login
#attr = cn

# User provisioning configuration
#[provisioning]
#method = externalldap

# externalldap provisioner configuration
#[provisioning_externalldap]
# Login list that won't be provisioned with this provisioner
#exclude = root
# These attributes are mandatory to create a user
#ldap_uid = cn
#ldap_givenName = sn
#ldap_sn = sn
# Other attributes to fill in
#ldap_mail = mail
#...
