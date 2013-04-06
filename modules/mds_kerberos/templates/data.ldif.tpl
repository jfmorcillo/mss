dn: ou=kerberos,@SUFFIX@
ou: kerberos
objectClass: organizationalUnit

dn: uid=kadmin,ou=System Accounts,@SUFFIX@
uid: kadmin
objectClass: account
objectClass: simpleSecurityObject
userPassword: @KADMINPASSWD@
description: Default bind DN for the Kerberos Administration server

dn: uid=kdc,ou=System Accounts,@SUFFIX@
uid: kdc
objectClass: account
objectClass: simpleSecurityObject
userPassword: @KDCPASSWD@
description: Default bind DN for the Kerberos KDC server

dn: cn=Kerberos Admins,ou=System Groups,@SUFFIX@
cn: Kerberos Admins
objectClass: groupOfNames
description: Members can write entries and attributes under ou=kerberos
owner: uid=kadmin,ou=System Accounts,@SUFFIX@
member: uid=kadmin,ou=System Accounts,@SUFFIX@

dn: cn=Kerberos Readers,ou=System Groups,@SUFFIX@
cn: Kerberos Readers
objectClass: groupOfNames
description: Members can read entries and attributes under ou=kerberos
owner: uid=kadmin,ou=System Accounts,@SUFFIX@
member: uid=kdc,ou=System Accounts,@SUFFIX@
