#!/bin/bash

# set -e

# Pykota installation script

### INCLUDES
. ../functions.sh

### BASIC CHECKS
check_mmc_configured

### DEFINITIONS
PYKOTA_HOME=/etc/pykota
SLAPPASSWD="/usr/sbin/slappasswd"
SLAPADD="/usr/sbin/slapadd"
SLAPD_CONF="/etc/openldap/slapd.conf"

### Create user directory
if [ ! -d ${PYKOTA_HOME} ]; then
    adduser --system -m --home-dir ${PYKOTA_HOME} pykota
    chown -R pykota.pykota ${PYKOTA_HOME}
    chmod 751 ${PYKOTA_HOME}
fi

### LDAP CONFIGURATION
# Copy the LDAP schema
add_schema /usr/share/pykota/ldap/pykota.schema

# Add LDAP indexes for PyKota
backup $SLAPD_CONF
grep -q 'pykota indexes' $SLAPD_CONF
if [ $? -ne 0 ]; then
    echo "Adding ldap indexes..."
    sed -i 's!index\tobjectClass\t\t\t\t\teq!index\tobjectClass\t\t\t\t\teq\n# pykota indexes\nindex\tpykotaUserName\t\t\t\t\tpres,eq,sub\nindex\tpykotaGroupName\t\t\t\t\tpres,eq,sub\nindex\tpykotaPrinterName\t\t\t\tpres,eq,sub\nindex\tpykotaBillingCode\t\t\t\tpres,eq,sub\nindex\tpykotaLastJobIdent\t\t\t\teq!' /etc/openldap/slapd.conf
    stop_service slapd
    slapindex
    restart_service slapd
fi

grep -q 'pykota limits' $SLAPD_CONF
if [ $? -ne 0 ]; then
    echo "Setting up ldap limits..."
    echo "" >> /etc/openldap/slapd.conf
    echo "# pykota limits" >> /etc/openldap/slapd.conf
    echo "limits dn=\"uid=LDAP Admin,ou=System Accounts,$MDSSUFFIX\" size.soft=-1 size.hard=soft" >> /etc/openldap/slapd.conf
    echo "limits dn=\"uid=LDAP Admin,ou=System Accounts,$MDSSUFFIX\" size.soft=-1 size.hard=soft" >> /etc/openldap/slapd.conf
fi

PYKOTA_OU=`ldapsearch -x -h 127.0.0.1 -LLL ou=Pykota dn | tr -d '\n'`
if [ -z "$PYKOTA_OU" ]; then
    stop_service slapd
    echo "Provisionning LDAP for Pykota..."
    cp /usr/share/pykota/ldap/pykota-sample.ldif ${PYKOTA_HOME}/pykota.ldif
    sed -i '/The encrypted password/,+7d' ${PYKOTA_HOME}/pykota.ldif
    sed -i "s!dc=example,dc=com!$MDSSUFFIX!g" ${PYKOTA_HOME}/pykota.ldif
    sed -i '/ou=People/,+3d' ${PYKOTA_HOME}/pykota.ldif
    $SLAPADD  < ${PYKOTA_HOME}/pykota.ldif
    [ $? -ne 0 ] && error $"Failed to update the LDAP database." && exit 1
    rm -f ${PYKOTA_HOME}/pykota.ldif
    restart_service slapd
else
    echo "LDAP already provisionned for pykota"
fi


# Configuration of Pykota
# pykota.conf
cp -f /usr/share/pykota/conf/pykota.conf.sample ${PYKOTA_HOME}/pykota.conf

sed -i 's!\(storagebackend: pgstorage\)!#\1!' ${PYKOTA_HOME}/pykota.conf
sed -i 's!\(storageserver: localhost\)!#\1!' ${PYKOTA_HOME}/pykota.conf
sed -i 's!\(storagename: pykota\)!#\1!' ${PYKOTA_HOME}/pykota.conf
sed -i 's!\(storageuser : pykotauser\)!#\1!' ${PYKOTA_HOME}/pykota.conf
sed -i 's!\(storageuserpw : readonlypw\)!#\1!' ${PYKOTA_HOME}/pykota.conf
sed -i 's!#\(storagebackend: ldapstorage\)!\1!' ${PYKOTA_HOME}/pykota.conf
sed -i 's!#\(storageserver: ldap://ldap.example.com:389\)!storageserver: ldap://127.0.0.1:389!' ${PYKOTA_HOME}/pykota.conf
sed -i 's!#\(storagename: dc=example,dc=com\)!\1!' ${PYKOTA_HOME}/pykota.conf
sed -i "s!#\(storageuser:\) cn=pykotauser,dc=example,dc=com!\1 uid=LDAP Admin,ou=System Accounts,dc=example,dc=com!" ${PYKOTA_HOME}/pykota.conf
sed -i "s!#\(storageuserpw:\) ls88DT5j!\1 $MDSPASS!" ${PYKOTA_HOME}/pykota.conf
sed -i "s!#\(userbase: ou=People,dc=example,dc=com\)!\1!" ${PYKOTA_HOME}/pykota.conf
sed -i "s!#\(userrdn: uid\)!\1!" ${PYKOTA_HOME}/pykota.conf
sed -i "s!#\(balancebase: ou=People,dc=example,dc=com\)!\1!" ${PYKOTA_HOME}/pykota.conf
sed -i "s!#\(balancerdn: uid\)!\1!" ${PYKOTA_HOME}/pykota.conf
sed -i "s!#\(groupbase: ou=Groups,dc=example,dc=com\)!\1!" ${PYKOTA_HOME}/pykota.conf
sed -i "s!#\(grouprdn: cn\)!\1!" ${PYKOTA_HOME}/pykota.conf
sed -i "s!#\(printerbase: ou=Printers,ou=PyKota,dc=example,dc=com\)!\1!" ${PYKOTA_HOME}/pykota.conf
sed -i "s!#\(printerrdn: cn\)!\1!" ${PYKOTA_HOME}/pykota.conf
sed -i "s!#\(jobbase: ou=Jobs,ou=PyKota,dc=example,dc=com\)!\1!" ${PYKOTA_HOME}/pykota.conf
sed -i "s!#\(lastjobbase: ou=LastJobs,ou=PyKota,dc=example,dc=com\)!\1!" ${PYKOTA_HOME}/pykota.conf
sed -i "s!#\(billingcodebase: ou=BillingCodes,ou=PyKota,dc=example,dc=com\)!\1!" ${PYKOTA_HOME}/pykota.conf
sed -i "s!#\(userquotabase: user\)!\1!" ${PYKOTA_HOME}/pykota.conf
sed -i "s!#\(userquotabase: ou=UQuotas,ou=PyKota,dc=example,dc=com\)!\1!" ${PYKOTA_HOME}/pykota.conf
sed -i "s!#\(groupquotabase: group\)!\1!" ${PYKOTA_HOME}/pykota.conf
sed -i "s!#\(groupquotabase: ou=GQuotas,ou=PyKota,dc=example,dc=com\)!\1!" ${PYKOTA_HOME}/pykota.conf
sed -i "s!#\(newuser : below\)!newuser : fail!" ${PYKOTA_HOME}/pykota.conf
sed -i "s!#newgroup : below!newgroup : fail!" ${PYKOTA_HOME}/pykota.conf
sed -i "s!#\(usermail : mail\)!usermail : mail!" ${PYKOTA_HOME}/pykota.conf
sed -i "s!#\(groupmembers: memberUid\)!groupmembers: memberUid!" ${PYKOTA_HOME}/pykota.conf
sed -i "s!example.com!$DOMAIN!" ${PYKOTA_HOME}/pykota.conf
sed -i "s!dc=example,dc=com!$MDSSUFFIX!" ${PYKOTA_HOME}/pykota.conf
sed -i "s!\(admin:\) .*!\1 root!" ${PYKOTA_HOME}/pykota.conf
sed -i "s!\(adminmail:\) .*!\1 admin@${DOMAIN}!" ${PYKOTA_HOME}/pykota.conf

# pykotadmin.conf
cp /usr/share/pykota/conf/pykotadmin.conf.sample ${PYKOTA_HOME}/pykotadmin.conf
sed -i 's!\(storageadmin : pykotaadmin\)!#\1!' ${PYKOTA_HOME}/pykotadmin.conf
sed -i 's!\(storageadminpw : readwritepw\)!#\1!' ${PYKOTA_HOME}/pykotadmin.conf
sed -i "s!# \(storagebackend: ldapstorage\)!\1!" ${PYKOTA_HOME}/pykotadmin.conf
sed -i "s!# \(storageserver: ldap://ldapmaster.example.com:389\)!storageserver: ldap://127.0.0.1:389!" ${PYKOTA_HOME}/pykotadmin.conf
sed -i "s!# \(storageadmin:\) cn=pykotaadmin,dc=example,dc=com!\1 uid=LDAP Admin,ou=System Accounts,dc=example,dc=com!" ${PYKOTA_HOME}/pykotadmin.conf
sed -i "s!# \(storageadminpw:\) BlfUPg7t!\1 $MDSPASS!" ${PYKOTA_HOME}/pykotadmin.conf
sed -i "s!dc=example,dc=com!$MDSSUFFIX!" ${PYKOTA_HOME}/pykotadmin.conf


### Fix persmissions
#chmod 644 ~pykota/pykota.conf
#chmod 640 ~pykota/pykotadmin.conf

# Link to CUPS server
[ ! -L /usr/lib/cups/backend/cupspykota ] && ln -s /usr/share/pykota/cupspykota /usr/lib/cups/backend/cupspykota
chmod 700 /usr/share/pykota/cupspykota
restart_service cups

# CGI scripts configuration
htpasswd -b -c -s /usr/share/pykota/cgi-bin/.htpasswd root ${MDSPASS}
cp -f templates/httpd/pykota.conf /etc/httpd/conf/webapps.d
cp -f /usr/share/pykota/stylesheets/pykota.css /var/www/html/
restart_service httpd

# Pykota Documentation
mkdir -p /var/www/html/Documentations
[ ! -L /var/www/html/Documentations/pykota ] && ln -s /usr/share/doc/pykota/html /var/www/html/Documentations/pykota

info_b $"Pykota is now ready and configured."
info $"You can access reporting web pages at http://@HOSTNAME@/pykota/ with login 'root' and password '$MDSPASS'."
info $"Your installation may be configured on the commandline. The Pykota documentation is available at http://@HOSTNAME@/Documentations/pykota"
