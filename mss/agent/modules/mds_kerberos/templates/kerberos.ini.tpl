[main]
disable = 0
realm = @REALM@
krb5Conf = /etc/krb5.conf 
kdcConf = /etc/kerberos/krb5kdc/kdc.conf

[kdc]
lockfile = /var/lock/subsys/krb5kdc
init = /etc/init.d/krb5kdc

[kadmin]
lockfile = /var/lock/subsys/kadmin
init = /etc/init.d/kadmin

                                                     