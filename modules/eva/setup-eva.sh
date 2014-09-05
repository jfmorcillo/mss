# Copyright Mandriva 2013 all rights reserved
#!/bin/bash

. '../functions.sh'

check_mmc_configured

# Backend

jbossInstanceIsRunning()
{	
	NB_INSTANCE=`ps -edf|grep $1|grep java|grep -v grep|wc -l`
	if [ $NB_INSTANCE -eq 0 ]
	then
		return 0
	else
		return 1
	fi
}

decryptLicense()
{
    if [ $RET -ne 0 ]; then
        export LICENSE_DETAILS=$1
    else
        LICENSE_DETAILS=`java -Djboss.server.home.dir=$JBOSS_HOME/eva -cp $workspace/.tools/siveo-license-tools.jar:$workspace/.tools net.siveo.license.main.LicenseManagerMain -info`
        RET=$?
        
        if [ $RET -eq 0 ]; then
            export LICENSE_DETAILS=$LICENSE_DETAILS
        else
            export LICENSE_DETAILS=$1
        fi
    fi
}

function get_interface_addr() {
  iface=`grep 'lan\|wan' /etc/shorewall/interfaces |cut -f 2 -d ' '`
  echo `ip addr show $iface | grep -o "inet [0-9]*\.[0-9]*\.[0-9]*\.[0-9]*" | sed 's/inet //'`
}

default_workspace="/usr/share/eva"
version_eva="3.0.0-SNAPSHOT"
fichier_zip="eVA-backend-install-${version_eva}.zip"
fichier_log=`pwd`"/${0%.*}.log"
default_language="fr"
default_modeInstallation="standalone"

HOMEPAGE="/var/lib/mss/local/eva/templates/homepage.tar.bz2"

pushd /var/www/html
    tar xjvf $HOMEPAGE
popd
sed -i "s/access MSS on/access eVA on/g" /etc/profile.d/99info.sh
sed -i "s/:8000//g" /etc/profile.d/99info.sh

postgresql_home="/var/lib/pgsql"

USE_ORACLE=1
if [ $USE_ORACLE -eq 0 ]; then
    default_rep_javahome="/usr/share/java"
else
    default_rep_javahome="/usr/java/jdk1.7.0_65"
fi

javaVersion64bits="jdk1.7.0_06"

default_rep_jboss="/opt/jboss-as"
versionJboss="jboss-as-7.1.1.Final"
export JBOSS_HOME=${default_rep_jboss}


#versionAnt="apache-ant-1.8.4"

default_rep_guacamole="/etc/guacamole"

codeActivationFile="/etc/ssl/private/siveo.sc"

export JAVA_HOME=$default_rep_javahome

eVA_adminUser="evaadmin"
password_eva=$1

iface_addr=`get_interface_addr`

export language="en"

if [ $USE_ORACLE -eq 1 ]; then
    mkdir /tmp/oracle
    pushd /tmp/oracle
    if [ ! -e "jdk-7u65-linux-x64.rpm" ] ; then
        wget --no-check-certificate --no-cookies --header "Cookie: oraclelicense=accept-securebackup-cookie" http://download.oracle.com/otn-pub/java/jdk/7u65-b17/jdk-7u65-linux-x64.rpm
    fi
    urpmi ./jdk-7u65-linux-x64.rpm
    popd
    sed -i '/JNI_LIBDIR/d' /etc/java/java.conf
    echo JNI_LIBDIR="/usr/java/jdk1.7.0_65/" >> /etc/java/java.conf
    sed -i '/JAVA_LIBDIR/d' /etc/java/java.conf
    echo JAVA_LIBDIR="/usr/java/jdk1.7.0_65/" >> /etc/java/java.conf
    sed -i '/JVM_ROOT/d' /etc/java/java.conf
    echo JVM_ROOT="/usr/java/jdk1.7.0_65/" >> /etc/java/java.conf
fi

if [ -f "$default_workspace" ]; then
    mkdir -p $default_workspace
fi

export modeInstallation=$default_modeInstallation
export workspace=$default_workspace

# Create evaadmin user
python ./mmc_createuser.py -l $eVA_adminUser -p $password_eva

# Create eva account for libvirt
echo eVA_KvM@dm1n | saslpasswd2 -p -a libvirt eva

if [ -e $JBOSS_HOME/eva/license/license.details ]; then
    export LICENSE_DETAILS=$JBOSS_HOME/eva/license/license.details
    decryptLicense $JBOSS_HOME/eva/license/license.details
fi

if [ -e $codeActivationFile ]; then
    export CODE_ACTIVATION=$codeActivationFile
fi


#postgresql

echo "Configure postgreSQL"

cp $postgresql_home/data/pg_hba.conf $postgresql_home/data/pg_hba.conf.$DATE_EXEC
echo "host    all         all         127.0.0.1/32          password" >> $postgresql_home/data/pg_hba.conf

chown postgres:postgres $postgresql_home/data/pg_hba.conf
backup $postgresql_home/data/pg_hba.conf
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" $postgresql_home/data/postgresql.conf
sed -i "s/#max_prepared_transactions = 0/max_prepared_transactions = 50/g" $postgresql_home/data/postgresql.conf
sed -i "s/ssl = true/ssl = false/g" $postgresql_home/data/postgresql.conf
chown postgres:postgres $postgresql_home/data/postgresql.conf
backup $postgresql_home/data/postgresql.conf
sed -i "s/max_connections = 100/max_connections = 50/g" $postgresql_home/data/postgresql.conf

#Configure Java
export PATH=$JAVA_HOME/bin:$PATH
echo "JAVA_HOME=$JAVA_HOME" >> /etc/java/java.conf

echo "export JAVA_HOME=$JAVA_HOME" >> ~eva/.bashrc
echo 'export PATH=$JAVA_HOME/bin:$PATH'  >> ~eva/.bash_profile

    # création d'un repertoire /var/log/jboss-as avec les droits pour eva:siveo
        mkdir -p /var/log/jboss-as
        mkdir -p /var/run/jboss-as
        chown -R eva:siveo /var/log/jboss-as
        chown -R eva:root /var/run/jboss-as

   #Modification des droits

       sed -i '/JBOSS_HOME=/d' ~/.bash_profile
       echo "export JBOSS_HOME=${jbosshomedir}" >> ~/.bash_profile
       echo "export JBOSS_EVA=${jbosshomedir}/eva" >> ~/.bash_profile
       echo "export JBOSS_ADMIN=${jbosshomedir}/eva-admin" >> /root/.bash_profile
       echo "export JBOSS_REPORTING=${jbosshomedir}/eva-reporting" >> ~/.bash_profile
       echo "export JBOSS_GUACAMOLE=${jbosshomedir}/guacamole" >> ~/.bash_profile

       sed -i '/JBOSS_HOME=/d' ~eva/.bashrc
       echo "export JAVA_HOME=$JAVA_HOME" >> ~eva/.bashrc
       echo "export PATH=\$JAVA_HOME/bin:\$PATH" >> ~eva/.bashrc
       echo "export JBOSS_HOME=${jbosshomedir}" >> ~eva/.bashrc
       echo "export JBOSS_EVA=\$JBOSS_HOME/eva" >> ~eva/.bashrc
       echo "export JBOSS_ADMIN=\$JBOSS_HOME/eva-admin" >> ~eva/.bashrc
       echo "export JBOSS_REPORTING=\$JBOSS_HOME/eva-reporting" >> ~eva/.bashrc
       echo "export JBOSS_GUACAMOLE=\$JBOSS_HOME/guacamole" >> ~eva/.bashrc
       sed -i '/JBOSS_HOME=/d' ~eva/.bash_profile 
       echo "export JAVA_HOME=$JAVA_HOME" >> ~eva/.bash_profile
       echo "export PATH=\$JAVA_HOME/bin:\$PATH" >> ~eva/.bash_profile
       echo "export JBOSS_HOME=${jbosshomedir}" >> ~eva/.bash_profile
       echo "export JBOSS_EVA=\$JBOSS_HOME/eva" >> ~eva/.bash_profile
       echo "export JBOSS_ADMIN=\$JBOSS_HOME/eva-admin" >> ~eva/.bash_profile
       echo "export JBOSS_REPORTING=\$JBOSS_HOME/eva-reporting" >> ~eva/.bash_profile
       echo "export JBOSS_GUACAMOLE=\$JBOSS_HOME/guacamole" >> ~eva/.bash_profile

       cd /etc/init.d
       rm -f jboss-eva-admin
       rm -f jboss-eva-reporting
       rm -f jboss-eva
       rm -f jboss-guacamole
       ln -s ${jbosshomedir}/bin/init.d/jboss-as-eva-admin.sh jboss-eva-admin
       ln -s ${jbosshomedir}/bin/init.d/jboss-as-eva-reporting.sh jboss-eva-reporting
       ln -s ${jbosshomedir}/bin/init.d/jboss-as-eva.sh jboss-eva
       ln -s ${jbosshomedir}/bin/init.d/jboss-as-guacamole.sh jboss-guacamole
       chkconfig --level 2345 jboss-eva on
       chkconfig --level 2345 jboss-eva-admin on
       chkconfig --level 2345 jboss-eva-reporting on
       chkconfig --level 2345 jboss-guacamole on

       cp $workspace/.guacamole/guacamole.properties $JBOSS_HOME/modules/net/siveo/guacamole/main/properties/guacamole.properties
       sed -i "s/@GUACD_SERVER@/localhost/g" $JBOSS_HOME/modules/net/siveo/guacamole/main/properties/guacamole.properties
       sed -i "s/@GUACD_PORT@/4822/g" $JBOSS_HOME/modules/net/siveo/guacamole/main/properties/guacamole.properties


# Install eVA	

echo "Install eVA"
	# mise en place de variables intermédiaires
	export JBOSS_EVA=${JBOSS_HOME}/eva
	export JBOSS_ADMIN=${JBOSS_HOME}/eva-admin
	export JBOSS_REPORTING=${JBOSS_HOME}/eva-reporting
	
    export passwordForUserSiveo=$password_eva
     	  
    cp ${workspace}/.eva/createdb.sql ${workspace}/.eva/createdb.sql.parse
    sed -i "s/@PASSWORD@/${passwordForUserSiveo}/g" ${workspace}/.eva/createdb.sql.parse
        	  
    cp ${workspace}/.eva/activiti.cfg.xml.generique ${workspace}/.eva/activiti.cfg.xml
    sed -i "s/@PASSWORD@/${passwordForUserSiveo}/g" ${workspace}/.eva/activiti.cfg.xml
        	  
    echo "localhost:5432:*:siveo:${passwordForUserSiveo}" >> ~/.pgpass
    chmod 600 ~/.pgpass

    JBOSS_ENCRYPTED_PASSWORD=`java -cp ${workspace}/.tools/siveo-persistence-jpa.jar:${workspace}/.tools/log4j-1.2.16.jar:${workspace}/.tools net.siveo.eva.domain.security.Crypt crypt ${passwordForUserSiveo}`
        	  
    cp ${workspace}/.jboss/eva.xml $JBOSS_EVA/configuration/eva.xml
    sed -i "s/@PASSWORD_SIVEO@/${JBOSS_ENCRYPTED_PASSWORD}/g" $JBOSS_EVA/configuration/eva.xml
        	  
    cp ${workspace}/.jboss/eva-admin.xml $JBOSS_ADMIN/configuration/eva-admin.xml
    sed -i "s/@PASSWORD_SIVEO@/${JBOSS_ENCRYPTED_PASSWORD}/g" $JBOSS_ADMIN/configuration/eva-admin.xml
        	  
    cp ${workspace}/.jboss/eva-reporting.xml $JBOSS_REPORTING/configuration/eva-reporting.xml
    sed -i "s/@PASSWORD_SIVEO@/${JBOSS_ENCRYPTED_PASSWORD}/g" $JBOSS_REPORTING/configuration/eva-reporting.xml
        	  
		i="0"        
	
	echo $JBOSS_HOME|sed 's/\//\\\//g' > /tmp/jj
	JBOSS_HOME_BACKSLACHE=`cat /tmp/jj`
	cp ${workspace}/.eva/eva.backup ${workspace}/.eva/eva.backup.parse
	sed -i "s/@JBOSS_HOME@/$JBOSS_HOME_BACKSLACHE/g" ${workspace}/.eva/eva.backup.parse
	sed -i "s/@IPFRONTAL@/${iface_addr}/g" ${workspace}/.eva/eva.backup.parse


    restart_service postgresql

	# Creation des instances de base eva, activiti, eva-jms + creation du user siveo
	su postgres -c "psql -U postgres -f ${workspace}/.eva/createdb.sql.parse" > /dev/null
	
	# create tables for reporting-quartz instance database
	su postgres -c "psql -U siveo -d reporting-quartz -f ${workspace}/.eva/reporting-quartz.sql" > /dev/null
	
	# Creation des tables de l'instance eva + remplissage des tables
	su postgres -c "psql -U siveo -d eva -f ${workspace}/.eva/eva.backup.parse" > /dev/null
	rm -f ${workspace}/.eva/eva.backup.parse
	
	# Creation des tables de l'instance activiti
	su postgres -c "psql -U siveo -d activiti -f ${workspace}/.eva/eva-activiti.backup" > /dev/null
	
	# Creation des tables de l'instance eva-jms
	su postgres -c "psql -U siveo -d eva-jms -f ${workspace}/.eva/eva-jms.backup" > /dev/null

	# Creation des tables de reporting
	su postgres -c "psql -U siveo -d reporting -f ${workspace}/.eva/reporting.sql" > /dev/null

    rm -fv ~/.pgpass

	# Re-creation du lien "syspreps" entre l'admin et eVA
	pushd ${JBOSS_ADMIN}
	    rm -f syspreps
	    ln -s ${JBOSS_EVA}/syspreps syspreps
	popd
	
	# deploiement du fichier bar contenant les processus bpm
	pushd ${workspace}/.tools
	java -cp siveo-activiti-deployment.jar:${workspace}/.eva net.siveo.activiti.deploy.DeployHelper ${workspace}/.eva/artifacts/eva-process-activiti.zip >> ${fichier_log}
	# TODO A REMETTRE rm -f ${workspace}/.eva/activiti.cfg.xml
	popd
	
# End Install_eva

mkdir -p /etc/ssl/private
chown -R root:siveo /etc/ssl/private
chmod 711 /etc/ssl/private

###### END FIXME

restart_service guacd


# FrontEnd.

rep_siveo="/var/www/siveo"
default_workspace_front="/usr/share/eva/web"
rep_apache2="/etc/httpd"
adresseIPEva="127.0.0.1"

mkdir -p $rep_siveo
mkdir -p $default_workspace

# Create OpenSSL Certs
# FIXME: Need to customize ?
openssl req \
    -new \
    -newkey rsa:4096 \
    -days 365 \
    -nodes \
    -x509 \
    -subj "/C=FR/ST=FR/L=Paris/O=Mdv/CN=www.mandriva.com" \
    -keyout eva.key \
    -out eva.cert

cp $default_workspace_front/workers.properties $rep_apache2/conf/workers.properties
sed -i "s/@ADRESSEIPEVA@/${adresseIPEva}/g" $rep_apache2/conf/workers.properties
sed -i "s/#LoadModule asis_module modules\/mod_asis.so/LoadModule asis_module modules\/mod_asis.so/g" ${rep_apache2}/conf/httpd.conf
sed -i "s/ServerTokens OS/ServerTokens Prod/g" ${rep_apache2}/conf/httpd.conf
sed -i "s/ServerSignature On/ServerSignature Off/g" ${rep_apache2}/conf/httpd.conf

CONF="/var/lib/mss/local/eva/templates/eva.conf.tpl"
cp -fv $CONF $rep_apache2/conf/webapps.d/eva.conf
chown apache: $rep_apache2/conf/webapps.d/eva.conf

local=`ls -l /etc/localtime | awk 'BEGIN { FS="/"; OFS=""; } {print $(NF-1),"/",$NF}'`
sed -i -e "s~^;date.timezone.*$~date.timezone = ${local}~g" /etc/php.ini


pswdMysql=`grep password /root/.my.cnf |  cut -d\' -f2`

mysql -u root -p${pswdMysql} < $default_workspace_front/actibox_siveo.sql
unzip -d $rep_siveo -o $default_workspace_front/siveo-eva-ihm-*.zip > /dev/null
mkdir -p $rep_siveo/temp/cache/php

chmod ugo+rwx $rep_siveo/utils/
chmod ugo+rwx $rep_siveo/var/
chmod -R ugo+rwx $rep_siveo/temp/

cp $default_workspace_front/webservices.xml $rep_siveo/sites/evplanet-admin/webservices.xml
sed -i -e "s/https/http/g" $rep_siveo/sites/evplanet-admin/webservices.xml
cp $default_workspace_front/encode.php $default_workspace_front/encodeTemp.php
sed -i "s/password/${pswdMysql}/g" $default_workspace_front/encodeTemp.php

pswdMysqlcrypt=`php $default_workspace_front/encodeTemp.php`

cp $default_workspace_front/profils.copixdb.xml $rep_siveo/var/config/profils.copixdb.xml
sed -i "s/@PASSWORDMYSQL@/${pswdMysqlcrypt}/g" $rep_siveo/var/config/profils.copixdb.xml

cp $default_workspace_front/copixproperties.xml $rep_siveo/var/config
sed -i "s/@USEHTTPS@/False/g" $rep_siveo/var/config/copixproperties.xml

# Configure the Firewall
mss-add-shorewall-rule -a VNC/ACCEPT -t lan
mss-add-shorewall-rule -a VNC/ACCEPT -t wan

# Configure the product name
sed -i "s/^product_name =.*$/product_name = Mandriva Business Server eVA/g" /etc/mmc/plugins/base.ini

#FIXME: Siveo has to change the api to allow auth_tcp = sasl. For now we'll just allow unencrypted connections
sed -i "s/^auth_tcp.*$/auth_tcp = \"none\"/g" /etc/libvirt/libvirtd.conf

info_b $"eVA is now configured."
info $"- Username is $eVA_adminUser"
info $"- Password is $password_eva"
info $"Reboot to complete the configuration."

