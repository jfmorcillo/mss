# slapd.conf template
include	/usr/share/openldap/schema/core.schema
include	/usr/share/openldap/schema/cosine.schema
include	/usr/share/openldap/schema/corba.schema
include	/usr/share/openldap/schema/inetorgperson.schema
include	/usr/share/openldap/schema/java.schema
include	/usr/share/openldap/schema/krb5-kdc.schema
include /usr/share/openldap/schema/kerberosobject.schema
include	/usr/share/openldap/schema/nis.schema
include	/usr/share/openldap/schema/openldap.schema
include /usr/share/openldap/schema/autofs.schema
include /usr/share/openldap/schema/samba.schema
include /usr/share/openldap/schema/evolutionperson.schema
include /usr/share/openldap/schema/calendar.schema
include /usr/share/openldap/schema/sudo.schema
include /usr/share/openldap/schema/dyngroup.schema
include /usr/share/openldap/schema/ppolicy.schema
include /usr/share/openldap/schema/dnszone.schema
include /usr/share/openldap/schema/dhcp.schema

include	/etc/openldap/schema/local.schema

pidfile		/var/run/ldap/slapd.pid
argsfile	/var/run/ldap/slapd.args

moduleload	back_monitor.la
moduleload	back_bdb.la
moduleload	syncprov.la
moduleload	ppolicy.la
#moduleload	refint.la

TLSCertificateFile      /etc/pki/tls/certs/ldap.pem
TLSCertificateKeyFile   /etc/pki/tls/private/ldap.pem
TLSCACertificateFile    /etc/pki/tls/certs/ldap.pem

loglevel none

database	bdb
suffix		"@SUFFIX@"
directory	/var/lib/ldap

checkpoint 256 5
# 32Mbytes, can hold about 10k posixAccount entries
dbconfig set_cachesize 0 33554432 1
dbconfig set_lg_bsize 2097152
cachesize 1000
idlcachesize 3000

index	objectClass					eq
index	uidNumber,gidNumber,memberuid,member		eq
index	uid						eq,subinitial
index	cn,mail,surname,givenname			eq,subinitial
index	sambaSID					eq,sub
index	sambaDomainName,displayName,sambaGroupType	eq
index	sambaSIDList					eq
index	krb5PrincipalName				eq
index	uniqueMember					pres,eq
index	zoneName,relativeDomainName			eq
index	sudouser					eq,sub
index	entryCSN,entryUUID				eq
index	dhcpHWAddress,dhcpClassData			eq

overlay syncprov
syncprov-checkpoint 100 10
syncprov-sessionlog 100

overlay ppolicy
ppolicy_default "cn=default,ou=Password Policies,@SUFFIX@"

# uncomment if you want to automatically update group
# memberships when an user is removed from the tree
# Also uncomment the refint.la moduleload above
#overlay refint
#refint_attributes member
#refint_nothing "uid=LDAP Admin,ou=System Accounts,dc=example,dc=com"

authz-regexp "gidNumber=0\\\+uidNumber=0,cn=peercred,cn=external,cn=auth"
	"uid=Account Admin,ou=System Accounts,@SUFFIX@"
authz-regexp ^uid=([^,]+),cn=[^,]+,cn=auth$ uid=$1,ou=People,@SUFFIX@

include /etc/openldap/mandriva-dit-access.conf

database monitor
access to dn.subtree="cn=Monitor"
	by group.exact="cn=LDAP Monitors,ou=System Groups,@SUFFIX@" read
	by group.exact="cn=LDAP Admins,ou=System Groups,@SUFFIX@" read
	by * none
