# mandriva-dit-access.conf

limits group="cn=LDAP Replicators,ou=System Groups,@SUFFIX@"
	limit size=unlimited
	limit time=unlimited

limits group="cn=LDAP Admins,ou=System Groups,@SUFFIX@"
	limit size=unlimited
	limit time=unlimited

limits group="cn=Account Admins,ou=System Groups,@SUFFIX@"
	limit size=unlimited
	limit time=unlimited

# so we don't have to add these to every other acl down there
access to dn.subtree="@SUFFIX@"
	by group.exact="cn=LDAP Admins,ou=System Groups,@SUFFIX@" write
	by group.exact="cn=LDAP Replicators,ou=System Groups,@SUFFIX@" read
	by * break

# userPassword access
# shadowLastChange is here because it needs to be writable by the user because
# of pam_ldap, which will update this attr whenever the password is changed.
# And this is done with the user's credentials
access to dn.subtree="@SUFFIX@"
        attrs=shadowLastChange
        by self write
        by group.exact="cn=Account Admins,ou=System Groups,@SUFFIX@" write
        by * read
access to dn.subtree="@SUFFIX@"
	attrs=userPassword
	by group.exact="cn=Account Admins,ou=System Groups,@SUFFIX@" write
	by self write
	by anonymous auth
	by * none

# kerberos key access
# "by auth" just in case...
access to dn.subtree="@SUFFIX@"
        attrs=krb5Key
        by self write
        by group.exact="cn=Account Admins,ou=System Groups,@SUFFIX@" write
        by anonymous auth
        by * none

# password policies
access to dn.subtree="ou=Password Policies,@SUFFIX@"
	by group.exact="cn=Account Admins,ou=System Groups,@SUFFIX@" write
	by * read

# samba password attributes
# by self not strictly necessary, because samba uses its own admin user to
# change the password on the user's behalf
# openldap also doesn't auth on these attributes, but maybe some day it will
access to dn.subtree="@SUFFIX@"
	attrs=sambaLMPassword,sambaNTPassword
	by group.exact="cn=Account Admins,ou=System Groups,@SUFFIX@" write
	by anonymous auth
	by self write
	by * none
# password history attribute
# pwdHistory is read-only, but ACL is simplier with it here
access to dn.subtree="@SUFFIX@"
	attrs=sambaPasswordHistory,pwdHistory
	by self read
	by group.exact="cn=Account Admins,ou=System Groups,@SUFFIX@" write
	by * none

# pwdReset, so the admin can force an user to change a password
access to dn.subtree="@SUFFIX@"
	attrs=pwdReset
	by group.exact="cn=Account Admins,ou=System Groups,@SUFFIX@" write
	by * read

# group owner can add/remove/edit members to groups
access to dn.regex="^cn=[^,]+,ou=(System Groups|Group),@SUFFIX@$"
	attrs=member
	by dnattr=owner write
	by * break

# let the user change some of his/her attributes
access to dn.subtree="ou=People,@SUFFIX@"
	attrs=carLicense,homePhone,homePostalAddress,mobile,pager,telephoneNumber
	by self write
	by * break

# create new accounts
access to dn.regex="^([^,]+,)?ou=(People|Group|Hosts),@SUFFIX@$"
	attrs=children,entry
	by group.exact="cn=Account Admins,ou=System Groups,@SUFFIX@" write
	by * break
# access to existing entries
access to dn.regex="^[^,]+,ou=(People|Hosts|Group),@SUFFIX@$"
	by group.exact="cn=Account Admins,ou=System Groups,@SUFFIX@" write
	by * break

# sambaDomainName entry
access to dn.regex="^(sambaDomainName=[^,]+,)?@SUFFIX@$"
	attrs=children,entry,@sambaDomain,@sambaUnixIdPool
	by group.exact="cn=Account Admins,ou=System Groups,@SUFFIX@" write
	by * read

# samba ID mapping
access to dn.regex="^(sambaSID=[^,]+,)?ou=Idmap,@SUFFIX@$"
	attrs=children,entry,@sambaIdmapEntry
	by group.exact="cn=Account Admins,ou=System Groups,@SUFFIX@" write
	by group.exact="cn=IDMAP Admins,ou=System Groups,@SUFFIX@" write
	by * read

# global address book
# XXX - which class(es) to use?
access to dn.regex="^(.*,)?ou=Address Book,@SUFFIX@"
	attrs=children,entry,@inetOrgPerson,@evolutionPerson,@evolutionPersonList
	by group.exact="cn=Address Book Admins,ou=System Groups,@SUFFIX@" write
	by * read

# dhcp entries
# XXX - open up read access to anybody?
access to dn.sub="ou=dhcp,@SUFFIX@"
	attrs=children,entry,@dhcpService,@dhcpServer,@dhcpSharedNetwork,@dhcpSubnet,@dhcpPool,@dhcpGroup,@dhcpHost,@dhcpClass,@dhcpSubClass,@dhcpOptions,@dhcpLeases,@dhcpLog
	by group.exact="cn=DHCP Admins,ou=System Groups,@SUFFIX@" write
	by group.exact="cn=DHCP Readers,ou=System Groups,@SUFFIX@" read
	by * read

# sudoers
access to dn.regex="^([^,]+,)?ou=sudoers,@SUFFIX@$"
	attrs=children,entry,@sudoRole
	by group.exact="cn=Sudo Admins,ou=System Groups,@SUFFIX@" write
	by * read

# dns
access to dn="ou=dns,@SUFFIX@"
	attrs=entry,@extensibleObject
	by group.exact="cn=DNS Admins,ou=System Groups,@SUFFIX@" write
	by * read
access to dn.sub="ou=dns,@SUFFIX@"
	attrs=children,entry,@dNSZone
	by group.exact="cn=DNS Admins,ou=System Groups,@SUFFIX@" write
	by group.exact="cn=DNS Readers,ou=System Groups,@SUFFIX@" read
	by * none

# MTA
# XXX - what else can we add here? Virtual Domains? With which schema?
## access to dn.one="ou=People,@SUFFIX@"
##	attrs=@inetLocalMailRecipient,mail
##	by group.exact="cn=MTA Admins,ou=System Groups,@SUFFIX@" write
## 	by * read

# KDE Configuration
access to dn.sub="ou=KDEConfig,@SUFFIX@"
	by group.exact="cn=KDEConfig Admins,ou=System Groups,@SUFFIX@" write
	by * read

# last one
access to dn.subtree="@SUFFIX@"
	by * read

