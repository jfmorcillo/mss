ldap-server "localhost";
ldap-port 389;
ldap-username "uid=LDAP Admin,ou=System Accounts,@SUFFIX@";
ldap-password "@PASSWORD@";
ldap-base-dn "@SUFFIX@";
ldap-dhcp-server-cn "@HOSTNAME@";
ldap-method dynamic;
ldap-debug-file "/var/log/dhcp-ldap-startup.log";
