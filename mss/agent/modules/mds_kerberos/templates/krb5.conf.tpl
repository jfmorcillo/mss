[logging]
 default = FILE:/var/log/kerberos/krb5libs.log
 kdc = FILE:/var/log/kerberos/krb5kdc.log
 admin_server = FILE:/var/log/kerberos/kadmind.log
  
[libdefaults]
 default_keytab_name = WRFILE:/etc/kerberos/krb5kdc/kadm5.keytab
 ticket_lifetime = 24h
 default_realm = @REALM@
 dns_lookup_realm = @DNSLOOKUPREALM@
 dns_lookup_kdc = @DNSLOOKUPKDC@
 forwardable = yes
 default_tgs_enctypes = @DEFAULTTGSENC@
 default_tkt_enctypes = @DEFAULTTKTENC@
 permitted_enctypes = @PERMITTEDENC@
 allow_weak_crypto = @ALLOWWEAK@
 clockskew = @CLOCK@

[realms]
 @REALM@ = {
  admin_server = @HOST@.@DNSDOMAIN@:@KADMIN_PORT@
@COMMENT@  kdc = @HOST@.@DNSDOMAIN@
  default_domain = @DNSDOMAIN@
  database_module = LDAP
 }

[domain_realm]
 @DNSDOMAIN@ = @REALM@
 .@DNSDOMAIN@ = @REALM@

[kdc]
 profile = /etc/kerberos/krb5kdc/kdc.conf

[pam]
 debug = false
 ticket_lifetime = 36000
 renew_lifetime = 36000
 forwardable = true
 krb4_convert = false

[login]
 krb4_convert = false
 krb4_get_tickets = false

[dbdefaults]
 ldap_kerberos_container_dn = "ou=kerberos,@SUFFIX@"
 
[dbmodules]
 LDAP = {
 db_library = kldap
 db_name = ldap
 ldap_kerberos_container_dn = ou=kerberos,@SUFFIX@
 ldap_kdc_dn ="uid=kdc,ou=System Accounts,@SUFFIX@"
 ldap_kadmind_dn ="uid=kadmin,ou=System Accounts,@SUFFIX@"
 ldap_service_password_file = /etc/kerberos/service.keyfile
 ldap_servers = ldapi://
 ldap_conns_per_server = 5
 }