#!/bin/bash
# (c) 2011 www.osinit.ru

function backup_database() {
    now=`date +%s`
    backupdir="/var/lib/ldap.$now"
    cp -a "$1" "$backupdir" 2>/dev/null
    if [ "$?" -ne "0" ]; then
        echo "Error, could not make a backup copy of the"
        echo "current LDAP database, aborting..."
        echo
        exit 1
    fi
    echo "$backupdir"
    return 0
}
                                                                                                                                                            
function generate_password() {
    pass=`date|md5sum|head -c 16`
    if [ "$?" -ne "0" ]; then
	echo "Error while generating password"
	exit 1
    fi
    echo "$pass"
    return 0
}


if [ "`id -u`" != "0" ]; then
	echo "Error, must be root user"
	exit 1
fi

. '../functions.sh'

#kerberos schema for LDAP 
kerberos_schema="templates/kerberos.schema"

#LDAP records for kerberos kdc and kadmin
data_template="templates/data.ldif.tpl"

#DNS data for kerberos - SRV and TXT records
#for adding
dns_data_template="templates/dns-data.ldif.tpl"
#for modifying
dns_data_modify_template="templates/dns-data-modify.ldif.tpl"

#LDAP acl
mandriva_dit_access_patch_template="templates/mandriva-dit-access.patch.tpl"

#kerberos configuration and acl files templates 
krb5_conf_template="templates/krb5.conf.tpl"
kdc_conf_template="templates/kdc.conf.tpl"
kadm5_acl_template="templates/kadm5.acl.tpl"

#patches for /etc/init.d/krb5kdc and /etc/init.d/kadmin
krb5kdc_init_patch="templates/krb5kdc-init.patch"
kadmin_init_patch="templates/kadmin-init.patch"

#kerberos.ini for mmc template
kerberos_ini_template="templates/kerberos.ini.tpl"

SLAPTEST="/usr/sbin/slaptest"
SLAPADD="/usr/sbin/slapadd"
LDAPMODIFY="/usr/bin/ldapmodify"
LDAPADD="/usr/bin/ldapadd"


mds_base_ini="/etc/mmc/plugins/base.ini"

if [ ! -f $mds_base_ini ]; then
    echo "2MMC interface is not installed"
    echo "2Aborting"
    exit 1
fi
            
suffix=`grep '^baseDN' $mds_base_ini | sed 's/^.*[[:space:]]\+=[[:space:]]\+//'`
adminpass=`grep '^password' $mds_base_ini | sed 's/^.*[[:space:]]\+=[[:space:]]\+//'`
            
#initial configure or reconfigure? realm name and database master key may not be reconfigured
`./check_configured.sh`
configured=$?

#realm name
realm="`echo $1|tr '[a-z]' '[A-Z]'`"
if [ "x$realm" = "x" ];then
    echo "2Realm name is empty"
    echo "2Aborting"
    exit 1
fi
 
#DNS domain name
dnsdomain="$2"
if [ "x$dnsdomain" = "x" ];then
    echo "2DNS domain name is empty"
    echo "2Aborting"
    exit 1
fi    

#KDC and administration server host name
kdchost="$3"
#KDC and administration server host name without domain name
kdchostname=`echo $kdchost |awk -F. '{ print $1 }'`
if [ "x$kdchostname" = "x" ];then
    echo "2KDC host name is empty"
    echo "2Aborting"
    exit 1
fi    

#KDC port number
kdcport="$4"
if [ "x$kdcport" = "x" ];then
    echo "1KDC port number is empty. Default port, 88, is used"
    kdcport="88"
fi    

#administration server port number
kadminport="$5"
if [ "x$kadminport" = "x" ];then
    echo "1Administration server port number is empty. Default port, 749, is used"
    kadminport="749"
fi    

#port for password changing
kpasswdport=464
#KDC database master key
kdcmasterkey="$6"
if [ "$configured" = "0" ];then
    if [ "x$kdcmasterkey" = "x" ];then
        echo "2KDC database master key is empty"
	echo "2Aborting"
	exit 1
    fi  
fi    

#DNS lookup for KDC
dnslookupkdc="${7}"
if [ "$dnslookupkdc" = "on" ];then
    dnslookupkdc="true"
else
    dnslookupkdc="false"
fi  

#DNS lookup for realm
dnslookuprealm="${8}"
if [ "$dnslookuprealm" = "on" ];then
    dnslookuprealm="true"
else
    dnslookuprealm="false"
fi  

DEFAULTENC="des3-cbc-sha1-kd des-cbc-crc"

#supported list of session key encryption types that should be returned by the KDC
defaulttgsenc="${9}"
if [ "x$defaulttgsenc" = "x" ];then
    defaulttgsenc="$DEFAULTENC"
fi  

#supported list of session key encryption types that should be requested by the client
defaulttktenc="${10}"
if [ "x$defaulttktenc" = "x" ];then
    defaulttktenc="$DEFAULTENC"
fi  

#all encryption types that are permitted for use in session key encryption
permittedenc="${11}"
if [ "x$permittedenc" = "x" ];then
    permittedenc="$DEFAULTENC"
fi  

#if set to 0 (for false), then weak encryption types will be filtered out
allowweak="${12}"
if [ "$allowweak" = "on" ];then
    allowweak="true"
else
    allowweak="false"
fi  

#maximum allowable amount of clockskew in seconds
clock="${13}"
if [ "x$clock" = "x" ];then
    clock="300"
fi  

#initial configure or reconfigure? realm name and database master key may not be reconfigured

if [ "$configured" = "0" ]; then
    echo "0Configuring kerberos..."
else
    echo "0Reconfiguring kerberos..."
fi

#: << 'COM1'

#KDC host is LDAP server
#ldaphost=`hostname -f`
ldaphost="$kdchostname.$dnsdomain" 

#copying kerberos.schema 

cp -f $kerberos_schema /etc/openldap/schema
if [ $? -ne 0 ]; then 
    echo "2Error while copying kerberos.schema in# /etc/openldap/schema";
    echo "2Aborting"
    exit 1
fi

# if kerberos.schema is not included, add it to slapd.conf

backup /etc/openldap/slapd.conf
myslapdconf=`make_temp`

res=`cat /etc/openldap/slapd.conf|grep "^include /etc/openldap/schema/kerberos.schema"`
if [ "x$res" = "x" ]; then 
    cat /etc/openldap/slapd.conf|sed -e "\/include \/etc\/openldap\/schema\/mmc.schema/a \include \/etc\/openldap\/schema\/kerberos.schema" >$myslapdconf
else
    cat /etc/openldap/slapd.conf >$myslapdconf    
fi
    
chmod 0640 $myslapdconf
chgrp ldap $myslapdconf

#/etc/sysconfig/ldap - configure slapd to listen local socket 

mysysconfigldap=`make_temp`

cat /etc/sysconfig/ldap | sed -e "\
s/^.*SLAPDURLLIST.*$/SLAPDURLLIST=\"ldap:\/\/\/ ldaps:\/\/\/ ldapi:\/\/\/\"/" > $mysysconfigldap
                
chmod 0640 $mysysconfigldap
chgrp ldap $mysysconfigldap

#test openldap configuration

$SLAPTEST -u -f $myslapdconf > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "2Error generating OpenLDAP configuration file"
    echo "2Aborting. File used was# $myslapdconf"
    exit 1
else
    echo "7OpenLDAP configuration file is generated successfully"
fi

##generate passwords for kdc and kadmin
kdc_passwd=`generate_password`
kadmin_passwd=`generate_password`


if [ "$configured"="0" ]; then
    #only if initial configure
    #ldif file for adding records for kerberos kdc and kadmin into LDAP
    
    tmpdataldif=`make_temp`

    cat $data_template | sed -e "\
    s/@SUFFIX@/$suffix/g;
    s/@KADMINPASSWD@/$kadmin_passwd/g;\
    s/@KDCPASSWD@/$kdc_passwd/g"> $tmpdataldif

    echo "0Loading kdc and kadmin data into database"

    # dry run first
    $SLAPADD -u -f $myslapdconf < $tmpdataldif
    #$LDAPADD -xvn -w "$adminpass" -D "uid=LDAP Admin,ou=System Accounts,$suffix" -f $tmpdataldif
    if [ $? -ne 0 ]; then
	echo "2Error loading kdc and kadmin data into database"
        echo "2Ldif file used:# $tmpdataldif"
        echo "2slapd.conf file used:# $myslapdconf"
        echo "2Aborting"
        exit 1
    else
    echo "7kdc and kadmin data is loaded into database"
    fi
fi

#dns plugin must be installed and configured

#check LDAP record of current DNS zone
echo "0Searching DNS zone in database..."
s=`ldapsearch -x -w "$adminpass" -D "uid=LDAP Admin,ou=System Accounts,$suffix" -LLL -b "ou=$dnsdomain,ou=$dnsdomain,ou=dns,$suffix" "(ou=$dnsdomain)"`
if [ "x$s" = "x" ]; then
    echo "2DNS zone is not found in database"
    echo "2Zone searched:# $dnsdomain"
    echo "2Aborting"
    exit 1
else
    echo "0DNS zone is found in database"
fi    

#check LDAP record of KDC host in current DNS zone
echo "0Searching KDC host record in DNS zone..."
s=`ldapsearch -x -w "$adminpass" -D "uid=LDAP Admin,ou=System Accounts,$suffix" -LLL -b "ou=$dnsdomain,ou=$dnsdomain,ou=dns,$suffix" "(relativeDomainName=$kdchostname)"`
if [ "x$s" = "x" ]; then
    echo "2KDC host is not found in DNS zone in database"
    echo "2Host checked:# $kdchostname"
    echo "2Zone containing the host:# $dnsdomain"
    echo "2Aborting"
    exit 1
else
    echo "0KDC host is found in DNS zone in database"
fi    

#check whether KDC host name can be resolved to an IP address
ip=`host -W 3s "$kdchostname.$dnsdomain"|grep 'address'|sed "s/ *//g;s/^.*address//g"`
if [ "x$ip" = "x" ]; then
    echo "2KDC host name cannot be resolved in IP address"
    echo "2Aborting"
    exit 1
fi

#check whether KDC host IP address can be resolved to a host name
h=`host -W 3s $ip|grep 'domain name pointer'|sed "s/ *//g;s/^.*pointer//g"`
if [ "x$h" = "x" ]; then
    echo "2KDC host IP address cannot be resolved to host name"
    echo "2Aborting"
    exit 1
fi

#check whether DNS SRV and TXT records are existed in current DNS zone
dns_configured="0"  

if [ "$configured" != "0" ]; then
    #check kerberos SRV records in current DNS zone

    k1=`ldapsearch -x -w "$adminpass" -D "uid=LDAP Admin,ou=System Accounts,$suffix" -LLL -b "ou=$dnsdomain,ou=$dnsdomain,ou=dns,$suffix" "(relativeDomainName=kerberos)"`
    k3=`ldapsearch -x -w "$adminpass" -D "uid=LDAP Admin,ou=System Accounts,$suffix" -LLL -b "ou=$dnsdomain,ou=$dnsdomain,ou=dns,$suffix" "(relativeDomainName=_kerberos._udp)"`
    k4=`ldapsearch -x -w "$adminpass" -D "uid=LDAP Admin,ou=System Accounts,$suffix" -LLL -b "ou=$dnsdomain,ou=$dnsdomain,ou=dns,$suffix" "(relativeDomainName=_kerberos-master._udp)"`
    k5=`ldapsearch -x -w "$adminpass" -D "uid=LDAP Admin,ou=System Accounts,$suffix" -LLL -b "ou=$dnsdomain,ou=$dnsdomain,ou=dns,$suffix" "(relativeDomainName=_kerberos-adm._tcp)"`
    k6=`ldapsearch -x -w "$adminpass" -D "uid=LDAP Admin,ou=System Accounts,$suffix" -LLL -b "ou=$dnsdomain,ou=$dnsdomain,ou=dns,$suffix" "(relativeDomainName=_kpasswd._udp)"`

    if [[ ("x$k1" != "x") && ("x$k3" != "x") && ("x$k4" != "x") && ("x$k5" != "x") && ("x$k6" != "x") ]]; then
	dns_configured="1"
    fi 
fi

#loading/modifying dns data in LDAP 
if [[ ("$dns_configured" = "0") || ("$configured" = "0") ]]; then
    #ldif file for adding DNS SRV records for kerberos into LDAP
    tmpdnsdataldif=`make_temp`

    cat $dns_data_template | sed -e "\
    s/@SUFFIX@/$suffix/g;\
    s/@REALM@/$realm/g;\
    s/@DNSDOMAIN@/$dnsdomain/g;\
    s/@HOST@/$kdchostname/g;\
    s/@KDC_PORT@/$kdcport/g;\
    s/@KADMIN_PORT@/$kadminport/g;\
    s/@KPASSWD_PORT@/$kpasswdport/g"> $tmpdnsdataldif

    echo "0Loading kerberos DNS data into database"
    $SLAPADD -u -f $myslapdconf < $tmpdnsdataldif
    #$LDAPADD -xvn -w "$adminpass" -D "uid=LDAP Admin,ou=System Accounts,$suffix" -f $tmpdnsdataldif
    if [ $? -ne 0 ]; then
        echo "2Error loading kerberos DNS data into database"
        echo "2Ldif file used:# $tmpdnsdataldif"
        echo "2slapd.conf file used:# $myslapdconf"
	echo "2Aborting"
        exit 1
    else
	echo "7Kerberos DNS data is loaded into database"
    fi

else
    #ldif file for modifying DNS SRV records for kerberos in LDAP
    tmpdnsdataldif=`make_temp`

    cat $dns_data_modify_template | sed -e "\
    s/@SUFFIX@/$suffix/g;\
    s/@REALM@/$realm/g;\
    s/@DNSDOMAIN@/$dnsdomain/g;\
    s/@HOST@/$kdchostname/g;\
    s/@KDC_PORT@/$kdcport/g;\
    s/@KADMIN_PORT@/$kadminport/g;\
    s/@KPASSWD_PORT@/$kpasswdport/g"> $tmpdnsdataldif

    echo "0Updating kerberos DNS data in database"

    # dry run first
    $LDAPMODIFY -x -w "$adminpass" -D "uid=LDAP Admin,ou=System Accounts,$suffix" -n -f $tmpdnsdataldif
        
    if [ $? -ne 0 ]; then
        echo "2Error updating kerberos DNS data in database"
        echo "2Ldif file used:# $tmpdnsdataldif"
        echo "2Aborting"
	exit 1
    else
	echo "7Kerberos DNS data is updated in database"
    fi
fi


#stop ldap and mmc-agent
/sbin/service ldap stop > /dev/null 2>&1
if [ $? -eq 0 ]; then echo "7Service ldap stopped successfully"
else echo "2Service ldap fails stopping. Check# /var/log/syslog"; exit 1
fi

/sbin/service mmc-agent stop > /dev/null 2>&1
if [ $? -eq 0 ]; then echo "7Service mmc-agent stopped successfully"
else echo "2Service mmc-agent fails stopping. Check# /var/log/mmc/mmc-agent"; exit 1
fi
                                                                                                                                                            
backup_db=`backup_database /var/lib/ldap`
backup_slapd_conf=`mybackup /etc/openldap/slapd.conf`
backup_sysconfig_ldap=`mybackup /etc/sysconfig/ldap`

cat $myslapdconf > /etc/openldap/slapd.conf; rm -f $myslapdconf
cat $mysysconfigldap > /etc/sysconfig/ldap; rm -f $mysysconfigldap


backup_db=`backup_database /var/lib/ldap`

if [ "$configured" = "0" ]; then
    # initial configure:

    echo "0Loading kdc and kadmin data into database..."

    $SLAPADD  < $tmpdataldif
    if [ $? -ne 0 ]; then
	echo "2Error loading kdc and kadmin data into database"
        echo "2Your previous database is at# $backup_db"
        echo "2Your original /etc/openldap/slapd.conf file was backed up as# $backup_slapd_conf"
        echo "2Your original /etc/sysconfig/ldap file was backed up as# $backup_sysconfig_ldap"
        echo "2Aborting"
	exit 1
    else
        echo "7kdc and kadmin data is loaded into database"
        echo "0Your previous database directory was backed up as# $backup_db"
    fi    
    
    #LDAP acls
    tmppatch=`make_temp`
    cat $mandriva_dit_access_patch_template | sed -e "\
    s/@SUFFIX@/$suffix/g;\
    s/@REALM@/$realm/g;" > $tmppatch
    backup_mandriva_dit_accesss_conf=`mybackup /etc/openldap/mandriva-dit-access.conf`

    echo "0Adding kerberos LDAP ACLs in# /etc/openldap/mandriva-dit-access.conf"
    patch -p0 /etc/openldap/mandriva-dit-access.conf -i $tmppatch
    chmod 0640 /etc/openldap/mandriva-dit-access.conf
    chgrp ldap /etc/openldap/mandriva-dit-access.conf
    echo "7Kerberos LDAP ACLs are added in# /etc/openldap/mandriva-dit-access.conf"
    
fi

if [ "$dns_configured" = "0" ]; then

    echo "0Loading kerberos DNS data into database..."
    $SLAPADD < $tmpdnsdataldif
    if [ $? -ne 0 ]; then
	echo "2Error loading kerberos DNS data into database"
        echo "2Your previous database is at# $backup_db"
        echo "2Your original /etc/openldap/slapd.conf file was backed up as# $backup_slapd_conf"
        echo "2Your original /etc/sysconfig/ldap file was backed up as# $backup_sysconfig_ldap"
        echo "2Aborting"
        exit 1
    else
	echo "7Kerberos DNS data is loaded into database"
        echo "0Your previous database directory was backed up as# $backup_db"
    fi
    
    #start ldap
    /sbin/service ldap start > /dev/null 2>&1
    if [ $? -eq 0 ]; then 
	echo "7Service ldap started successfully"
    else 
	echo "2Service ldap fails starting. Check# /var/log/syslog" 
        echo "2Aborting"
	exit 1
    fi
    
else
    #reconfigure dns:
    #start ldap and update dns data
    /sbin/service ldap start > /dev/null 2>&1
    if [ $? -eq 0 ]; then 
	echo "7Service ldap started successfully"
    else 
	echo "2Service ldap fails starting. Check# /var/log/syslog"
        echo "2Aborting"
	exit 1
    fi
    
    echo "0Updating kerberos DNS data in database..."
    
    $LDAPMODIFY -x -w "$adminpass" -D "uid=LDAP Admin,ou=System Accounts,$suffix" -f $tmpdnsdataldif
        
    if [ $? -ne 0 ]; then
        echo "2Error updating kerberos DNS data in database"
        echo "2Your previous database is at# $backup_db"
        echo "2Your original /etc/openldap/slapd.conf file was backed up as# $backup_slapd_conf"
        echo "2Your original /etc/sysconfig/ldap file was backed up as# $backup_sysconfig_ldap"
        echo "2Aborting"
	exit 1
    else
	echo "7Kerberos DNS data is updated in database"
	echo "7Your previous database directory was backed up as# $backup_db"
    fi
fi

# dns restart

/sbin/service named restart > /dev/null 2>&1
if [ $? -eq 0 ]; then 
    echo "7Service named restarted successfully"
else 
    echo "2Service named fails restarting. Check# /var/log/syslog"
    exit 1
fi

#Kerberos

#try stop just in case
/sbin/service krb5kdc stop > /dev/null 2>&1
/sbin/service kadmin stop > /dev/null 2>&1

###/etc/krb5.conf
backup /etc/krb5.conf

if [ $dnslookupkdc = "true" ];then
    comment="#"    
else
    comment=""    
fi    

cat $krb5_conf_template | sed -e "\
s/@SUFFIX@/$suffix/g;\
s/@REALM@/$realm/g;\
s/@HOST@/$kdchostname/g;\
s/@DNSDOMAIN@/$dnsdomain/g;\
s/@KADMIN_PORT@/$kadminport/g;\
s/@DNSLOOKUPREALM@/$dnslookuprealm/g;\
s/@DNSLOOKUPKDC@/$dnslookupkdc/g;\
s/@COMMENT@/$comment/g;\
s/@DEFAULTTGSENC@/$defaulttgsenc/g;\
s/@DEFAULTTKTENC@/$defaulttktenc/g;\
s/@PERMITTEDENC@/$permittedenc/g;\
s/@ALLOWWEAK@/$allowweak/g;\
s/@CLOCK@/$clock/g" > /etc/krb5.conf
       

###/etc/kerberos/krb5kdc/kdc.conf
backup /etc/kerberos/krb5kdc/kdc.conf
cat $kdc_conf_template | sed -e "\
s/@REALM@/$realm/;\
s/@KDC_PORT@/$kdcport/g" > /etc/kerberos/krb5kdc/kdc.conf

###/etc/kerberos/krb5kdc/kadm5.acl
cat $kadm5_acl_template > /etc/kerberos/krb5kdc/kadm5.acl
sed -i "s/\@REALM\@/$realm/" /etc/kerberos/krb5kdc/kadm5.acl

if [ "$configured" = "0" ]; then
    
    ###/etc/kerberos/krb5kdc/kadm5.keytab
    rm -f /etc/kerberos/krb5kdc/kadm5.keytab

    #patching /etc/init.d/krb5kdc and /etc/init.d/kadmin to start after ldap and named

    backup /etc/init.d/krb5kdc
    patch -p0 /etc/init.d/krb5kdc -i $krb5kdc_init_patch

    backup /etc/init.d/kadmin
    patch -p0 /etc/init.d/kadmin -i $kadmin_init_patch

    #create realm 
    echo "0Creating realm..."
    res=`kdb5_ldap_util -D "uid=LDAP Admin,ou=System Accounts,$suffix" -w $adminpass create -subtrees ou=kerberos,$suffix -P $kdcmasterkey -r $realm -s -H ldap://localhost| grep "Initializing database"`
    if [ "x$res" = "x" ]; then 
	echo "2Error creating realm"
	echo "2Aborting"
	exit 1
    else 
	echo "7Realm is created"
    fi

    #stash passwords for kdc and kadmin

    echo -en "$kdc_passwd\\n$kdc_passwd"|kdb5_ldap_util -D "cn=LDAP Admin,ou=System Accounts,$suffix" -w $adminpass stashsrvpw -f /etc/kerberos/service.keyfile "uid=kdc,ou=System Accounts,$suffix"
    if [ $? -ne 0 ]; then 
	echo "2Error stashing password for kdc"
        echo "2Aborting";
	exit 1
    fi

    echo -en "$kadmin_passwd\\n$kadmin_passwd"|kdb5_ldap_util -D "cn=LDAP Admin,ou=System Accounts,$suffix" -w $adminpass stashsrvpw -f /etc/kerberos/service.keyfile "uid=kadmin,ou=System Accounts,$suffix"
    if [ $? -ne 0 ]; then 
	echo "2Error stashing password for kadmin"
        echo "2Aborting";
	exit 1
    fi
    echo "7Passwords for kdc and kadmin are stashed"

    #stash system principals' passwords into default keytab file
    res=`kadmin.local -q "ktadd kadmin/admin kadmin/changepw"|grep "added"`
    if [ "x$res" == "x" ]; then 
        echo "2Error stashing password for system principals kadmin/admin and kadmin/changepw"
        echo "2Aborting";
	exit 1
    fi
    echo "7Passwords for system principals kadmin/admin and kadmin/changepw are stashed"

    #add default policy and ldap's principal ldap/{host}
    kadmin.local -q "add_policy -maxlife 180days -minlife 2days -minlength 5 -minclasses 1 default"
    
    echo "0Creating principal for KDC host# ldap/$ldaphost..."

    res=`kadmin.local -q "addprinc -randkey ldap/$ldaphost"|grep "created"`
    if [ "x$res" == "x" ]; then 
	echo "2Error creating principal for KDC host"
	echo "Principal:# ldap/$ldaphost"
        echo "2Aborting"
        exit 1
    fi

    #stash his password into default keytab file
        
    res=`kadmin.local -q  "ktadd ldap/$ldaphost"|grep "added"`
    if [ "x$res" == "x" ]; then 
        echo "2Error stashing password for KDC host principal"
        echo "Principal:# ldap/$ldaphost"
	echo "2Aborting"
        exit 1
    fi

    echo "7Principal for KDC host is created"


    #start kdc and kadmin
    /sbin/service krb5kdc start > /dev/null 2>&1
    if [ $? -eq 0 ]; then 
	echo "7Service krb5kdc started successfully"
    else 
	echo "2Service krb5kdc fails starting. Check# /var/log/syslog"
        exit 1
    fi

    /sbin/service kadmin start > /dev/null 2>&1
    if [ $? -eq 0 ]; then 
	echo "7Service kadmin started successfully"
    else 
	echo "2Service kadmin fails starting. Check# /var/log/syslog"
        exit 1
    fi
else
 # if reconfigure restart kdc and kadmin
    /sbin/service krb5kdc restart > /dev/null 2>&1
    if [ $? -eq 0 ]; then 
	echo "7Service krb5kdc restarted successfully"
    else 
	echo "2Service krb5kdc fails restarting. Check# /var/log/syslog"
        exit 1
    fi

    /sbin/service kadmin restart > /dev/null 2>&1
    if [ $? -eq 0 ]; then 
	echo "7Service kadmin restarted successfully"
    else 
	echo "2Service kadmin fails restarting. Check# /var/log/syslog"
        exit 1
    fi
fi

#kerberos.ini for mmc
backup /etc/mmc/plugins/kerberos.ini > /dev/null 2>&1

cat $kerberos_ini_template | sed -e "\
s/@REALM@/$realm/g" > /etc/mmc/plugins/kerberos.ini

if [ $? -eq 0 ]; then 
    echo "7MDS configuring done"
else 
    echo "2Error while configuring MDS# (/etc/mmc/plugins/kerberos.ini)"
    exit 1
fi

/sbin/service mmc-agent start > /dev/null 2>&1
if [ $? -eq 0 ]; then echo "7Service mmc-agent started successfully"
else echo "2Service mmc-agent fails starting. Check# /var/log/mmc/mmc-agent"; exit 1
fi

#COM1

echo "8Kerberos module is activated in the MDS interface"
echo "7You can add Kerberos principals from the MDS interface: https://@HOSTNAME@/mmc/"