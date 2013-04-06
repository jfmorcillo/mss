#!/bin/bash
# script checks whether realm is configured or not

mds_base_ini="/etc/mmc/plugins/base.ini"
[[ ! -f $mds_base_ini ]] && exit 1

suffix=`grep '^baseDN' $mds_base_ini | sed 's/^.*[[:space:]]\+=[[:space:]]\+//'`

kerberos_container=`ldapsearch -x -LLL -b "ou=kerberos,$suffix"`

if [ "x$kerberos_container" != "x" ]; then

    # find realm name in krb5.conf (default_realm in libdefaults section)
    realm=`cat /etc/krb5.conf|grep "default_realm"|sed "s/ *//g;s/default_realm=//g"`

    # find realm's container
    realm_container=`ldapsearch -x -LLL -b "cn=$realm,ou=kerberos,$suffix"`

    if [ "x$realm_container" != "x" ];then
        exit 1
    fi
fi
exit 0
