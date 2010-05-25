# base tree
dn: @SUFFIX@
dc: @DC@
objectClass: domain
objectClass: domainRelatedObject
associatedDomain: @DOMAIN@

dn: ou=People,@SUFFIX@
ou: People
objectClass: organizationalUnit

dn: ou=Group,@SUFFIX@
ou: Group
objectClass: organizationalUnit
description: Container for user accounts

dn: cn=users,ou=Group,@SUFFIX@
gidNumber: 100
description: Default group
objectClass: posixGroup
objectClass: top
cn: users


dn: ou=System Accounts,@SUFFIX@
ou: System Accounts
objectClass: organizationalUnit
description: Container for System and Services privileged accounts

dn: ou=System Groups,@SUFFIX@
ou: System Groups
objectClass: organizationalUnit
description: Container for System and Services privileged groups

dn: ou=Hosts,@SUFFIX@
ou: Hosts
objectClass: organizationalUnit
description: Container for Samba machine accounts

dn: ou=Idmap,@SUFFIX@
ou: Idmap
objectClass: organizationalUnit
description: Container for Samba Winbind ID mappings

dn: ou=Address Book,@SUFFIX@
ou: Address Book
objectClass: organizationalUnit
description: Container for global address book entries

dn: ou=sudoers,@SUFFIX@
ou: sudoers
objectClass: organizationalUnit
description: Container for sudo related entries

dn: ou=dhcp,@SUFFIX@
ou: dhcp
objectClass: organizationalUnit
description: Container for DHCP related entries

dn: ou=dns,@SUFFIX@
ou: dns
objectClass: organizationalUnit
description: Container for DNS related entries

dn: ou=KDEConfig,@SUFFIX@
ou: KDEConfig
objectClass: organizationalUnit
description: Container for KDE configuration profiles

dn: ou=default,ou=KDEConfig,@SUFFIX@
ou: default
objectClass: organizationalUnit
description: Default KDE configuration for all users

# System Accounts
dn: uid=Account Admin,ou=System Accounts,@SUFFIX@
uid: Account Admin
objectClass: account
objectClass: simpleSecurityObject
userPassword: {CRYPT}x
description: Account used to administer all users, groups, machines and general accounts

dn: uid=nssldap,ou=System Accounts,@SUFFIX@
uid: nssldap
objectClass: account
objectClass: simpleSecurityObject
userPassword: {CRYPT}x
description: Unprivileged account which can be used by nss_ldap for when anonymous searches are disabled

dn: uid=MTA Admin,ou=System Accounts,@SUFFIX@
uid: MTA Admin
objectClass: account
objectClass: simpleSecurityObject
userPassword: {CRYPT}x
description: Account used to administer email related attributes

dn: uid=DHCP Admin,ou=System Accounts,@SUFFIX@
uid: DHCP Admin
objectClass: account
objectClass: simpleSecurityObject
userPassword: {CRYPT}x
description: Account used to administer DHCP related entries and attributes

dn: uid=DHCP Reader,ou=System Accounts,@SUFFIX@
uid: DHCP Reader
objectClass: account
objectClass: simpleSecurityObject
userPassword: {CRYPT}x
description: Account used to read entries and attributes under ou=dhcp

dn: uid=DNS Admin,ou=System Accounts,@SUFFIX@
uid: DNS Admin
objectClass: account
objectClass: simpleSecurityObject
userPassword: {CRYPT}x
description: Account used to administer DNS related entries and attributes

dn: uid=DNS Reader,ou=System Accounts,@SUFFIX@
uid: DNS Reader
objectClass: account
objectClass: simpleSecurityObject
userPassword: {CRYPT}x
description: Account used to read entries and attributes under ou=dns

dn: uid=Sudo Admin,ou=System Accounts,@SUFFIX@
uid: Sudo Admin
objectClass: account
objectClass: simpleSecurityObject
userPassword: {CRYPT}x
description: Account used to administer Sudo related entries and attributes

dn: uid=Address Book Admin,ou=System Accounts,@SUFFIX@
uid: Address Book Admin
objectClass: account
objectClass: simpleSecurityObject
userPassword: {CRYPT}x
description: Account used to administer global Address Book related entries and attributes

dn: uid=LDAP Admin,ou=System Accounts,@SUFFIX@
uid: LDAP Admin
objectClass: account
objectClass: simpleSecurityObject
userPassword: @ldapadmin_password@
description: Account used to administer all parts of the Directory

dn: uid=LDAP Replicator,ou=System Accounts,@SUFFIX@
uid: LDAP Replicator
objectClass: account
objectClass: simpleSecurityObject
userPassword: {CRYPT}x
description: Account used by consumer servers for replication

dn: uid=LDAP Monitor,ou=System Accounts,@SUFFIX@
uid: LDAP Monitor
objectClass: account
objectClass: simpleSecurityObject
userPassword: {CRYPT}x
description: Account used to read cn=monitor entries

dn: uid=KDEConfig Admin,ou=System Accounts,@SUFFIX@
uid: KDEConfig Admin
objectClass: account
objectClass: simpleSecurityObject
userPassword: {CRYPT}x
description: Account used to administer ou=KDEConfig entries

dn: uid=Idmap Admin,ou=System Accounts,@SUFFIX@
uid: Idmap Admin
objectClass: account
objectClass: simpleSecurityObject
userPassword: {CRYPT}x
description: Account used to administer Samba Winbind ID mapping related entries and attributes

# Groups associated with system accounts
dn: cn=LDAP Admins,ou=System Groups,@SUFFIX@
cn: LDAP Admins
objectClass: groupOfNames
description: Members can administer all parts of the Directory
owner: uid=LDAP Admin,ou=System Accounts,@SUFFIX@
member: uid=LDAP Admin,ou=System Accounts,@SUFFIX@

dn: cn=Account Admins,ou=System Groups,@SUFFIX@
cn: Account Admins
objectClass: groupOfNames
description: Members can administer all user, group and machine accounts
owner: uid=Account Admin,ou=System Accounts,@SUFFIX@
member: uid=Account Admin,ou=System Accounts,@SUFFIX@

dn: cn=Sudo Admins,ou=System Groups,@SUFFIX@
cn: Sudo Admins
objectClass: groupOfNames
description: Members can administer ou=sudoers entries and attributes
owner: uid=Sudo Admin,ou=System Accounts,@SUFFIX@
member: uid=Sudo Admin,ou=System Accounts,@SUFFIX@

dn: cn=DNS Admins,ou=System Groups,@SUFFIX@
cn: DNS Admins
objectClass: groupOfNames
description: Members can administer ou=DNS entries and attributes
owner: uid=DNS Admin,ou=System Accounts,@SUFFIX@
member: uid=DNS Admin,ou=System Accounts,@SUFFIX@

dn: cn=DNS Readers,ou=System Groups,@SUFFIX@
cn: DNS Readers
objectClass: groupOfNames
description: Members can read entries and attributes under ou=dns
owner: uid=DNS Admin,ou=System Accounts,@SUFFIX@
member: uid=DNS Reader,ou=System Accounts,@SUFFIX@

dn: cn=DHCP Admins,ou=System Groups,@SUFFIX@
cn: DHCP Admins
objectClass: groupOfNames
description: Members can administer ou=DHCP entries and attributes
owner: uid=DHCP Admin,ou=System Accounts,@SUFFIX@
member: uid=DHCP Admin,ou=System Accounts,@SUFFIX@

dn: cn=DHCP Readers,ou=System Groups,@SUFFIX@
cn: DHCP Readers
objectClass: groupOfNames
description: Members can read entries and attributes under ou=dhcp
owner: uid=DHCP Admin,ou=System Accounts,@SUFFIX@
member: uid=DHCP Reader,ou=System Accounts,@SUFFIX@

dn: cn=Address Book Admins,ou=System Groups,@SUFFIX@
cn: Address Book Admins
objectClass: groupOfNames
description: Members can administer ou=Address Book entries and attributes
owner: uid=Address Book Admin,ou=System Accounts,@SUFFIX@
member: uid=Address Book Admin,ou=System Accounts,@SUFFIX@

dn: cn=LDAP Replicators,ou=System Groups,@SUFFIX@
cn: LDAP Replicators
objectClass: groupOfNames
description: Members can be used for syncrepl replication
owner: uid=LDAP Replicator,ou=System Accounts,@SUFFIX@
member: uid=LDAP Replicator,ou=System Accounts,@SUFFIX@

dn: cn=MTA Admins,ou=System Groups,@SUFFIX@
cn: MTA Admins
objectClass: groupOfNames
description: Members can administer email related attributes
owner: uid=MTA Admin,ou=System Accounts,@SUFFIX@
member: uid=MTA Admin,ou=System Accounts,@SUFFIX@

dn: cn=LDAP Monitors,ou=System Groups,@SUFFIX@
cn: LDAP Monitors
objectClass: groupOfNames
description: Members can read the cn=monitor backend
owner: uid=LDAP Monitor,ou=System Accounts,@SUFFIX@
member: uid=LDAP Monitor,ou=System Accounts,@SUFFIX@

dn: cn=Idmap Admins,ou=System Groups,@SUFFIX@
cn: Idmap Admins
objectClass: groupOfNames
description: Members can administer ou=Idmap entries and attributes
owner: uid=Idmap Admin,ou=System Accounts,@SUFFIX@
member: uid=Idmap Admin,ou=System Accounts,@SUFFIX@

dn: cn=KDEConfig Admins,ou=System Groups,@SUFFIX@
cn: KDEConfig Admins
objectClass: groupOfNames
description: Members can administer ou=KDEConfig entries and attributes
owner: uid=KDEConfig Admin,ou=System Accounts,@SUFFIX@
member: uid=KDEConfig Admin,ou=System Accounts,@SUFFIX@
member: uid=Account Admin,ou=System Accounts,@SUFFIX@

