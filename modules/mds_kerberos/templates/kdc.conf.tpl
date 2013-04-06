[kdcdefaults]
 acl_file = /etc/kerberos/krb5kdc/kadm5.acl
 
[realms]
 @REALM@ = {
  kdc_ports = @KDC_PORT@
  master_key_type = des3-hmac-sha1
  profile = /etc/krb5.conf
  acl_file = /etc/kerberos/krb5kdc/kadm5.acl
  key_stash_file = /etc/kerberos/krb5kdc/.k5.@REALM@
  max_life = 24h 0m 0s
  max_renewable_life = 7d 0h 0m 0s
 }
