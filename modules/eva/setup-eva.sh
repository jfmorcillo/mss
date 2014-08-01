# Copyright Mandriva 2013 all rights reserved
#!/bin/bash

. '../functions.sh'

check_mmc_configured

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

default_workspace="/usr/share/eva"
version_eva="3.0.0-SNAPSHOT"
fichier_zip="eVA-backend-install-${version_eva}.zip"
fichier_log=`pwd`"/${0%.*}.log"
default_language="fr"
default_modeInstallation="standalone"


postgresql_home="/var/lib/pgsql"
password_postgresql="siveo2014"

default_rep_javahome="/usr/share/java"
javaVersion64bits="jdk1.7.0_06"

default_rep_jboss="/opt/jboss-as"
versionJboss="jboss-as-7.1.1.Final"
export JBOSS_HOME=${default_rep_jboss}


#versionAnt="apache-ant-1.8.4"

default_rep_guacamole="/etc/guacamole"

codeActivationFile="/etc/ssl/private/siveo.sc"

export JAVA_HOME=$default_rep_javahome


default_language=$1
password_eva=$2
password_pg=$3
ipFrontal=127.0.0.1

#TODO: Add in desc.json ( choice between fr and en ).
#export language=$default_language
export language="fr"

if [ -f "$default_workspace" ]; then
    mkdir -p $default_workspace
fi

export modeInstallation=$default_modeInstallatio
export workspace=$default_workspace

# Add User/Group
USER="eva"
EVA=`grep $USER /etc/passwd`
GROUP="siveo"
SIVEO=`grep siveo /etc/group`

if [ -z $EVA ]; then 
    useradd $USER
    echo $password_eva | passwd eva --stdin
fi

if [ -z $SIVEO ]; then
    groupadd $GROUP
fi

if [ -e $JBOSS_HOME/eva/license/license.details ]; then
    export LICENSE_DETAILS=$JBOSS_HOME/eva/license/license.details
    decryptLicense $JBOSS_HOME/eva/license/license.details
fi

if [ -e $codeActivationFile ]; then
    export CODE_ACTIVATION=$codeActivationFile
fi


#postgresql

echo "Configure postgreSQL"

#FIXME: Change into  ${pswdPostgres}
su - postgres -c "psql -c \"ALTER USER postgres WITH PASSWORD '${password_pg}';\""

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
export JAVA_HOME=${javahomedir}
export PATH=$JAVA_HOME/bin:$PATH
echo "JAVA_HOME=$JAVA_HOME" >> /etc/java/java.conf

echo "export JAVA_HOME=${javahomedir}"  >> ~eva/.bash_profile
echo 'export PATH=$JAVA_HOME/bin:$PATH'  >> ~eva/.bash_profile

# Configure JBoss
jbosshomedir=$default_rep_jboss

pushd ${jbosshomedir}
binJboss=jboss-as-7.1.1.Final.tar.gz
    tar zxvf ${workspace}/.jboss/${binJboss} >> ${fichier_log}
    mkdir -p ${jbosshomedir}/eva-admin/deployments
    cp ${workspace}/.eva/artifacts/eva-admin.war ${jbosshomedir}/eva-admin/deployments
    mkdir -p ${jbosshomedir}/eva/deployments/eva
    cp ${workspace}/.eva/artifacts/siveo-eva-ear.ear ${jbosshomedir}/eva/deployments/eva
    mkdir -p ${jbosshomedir}/eva-reporting/deployments
    cp ${workspace}/.eva/artifacts/siveo-reporting-ws.war ${jbosshomedir}/eva-reporting/deployments
       
    rm -f ${jbosshomedir}/eva/GuestTools/*
    unzip ${workspace}/.eva/artifacts/Scripts-GuestTools.zip -d ${jbosshomedir}/eva/GuestTools/

    mkdir -p ${jbosshomedir}/modules/net/siveo/eva-cfg/main/properties
    cp ${workspace}/.jboss/siveo-reporting-ehcache.xml ${jbosshomedir}/modules/net/siveo/eva-cfg/main/properties/ehcache.xml
    echo "${jbosshomedir}/"|sed 's/\//\\\//g' > /tmp/jj
    JBOSS_HOME_BACKSLACHE=`cat /tmp/jj`
    # JBOSS_HOME_BACKSLACHE=${jbosshomedir}
    sed -i "s/@JBOSS_HOME@/$JBOSS_HOME_BACKSLACHE/g" ${jbosshomedir}/modules/net/siveo/eva-cfg/main/properties/ehcache.xml

    cp ${workspace}/.jboss/eva.conf ${jbosshomedir}/bin
    sed -i "s/@JBOSS_HOME@/$JBOSS_HOME_BACKSLACHE/g" ${jbosshomedir}/bin/eva.conf

    cp ${workspace}/.jboss/eva-admin.conf ${jbosshomedir}/bin
    sed -i "s/@JBOSS_HOME@/$JBOSS_HOME_BACKSLACHE/g" ${jbosshomedir}/bin/eva-admin.conf

    cp ${workspace}/.jboss/eva-reporting.conf ${jbosshomedir}/bin
    sed -i "s/@JBOSS_HOME@/$JBOSS_HOME_BACKSLACHE/g" ${jbosshomedir}/bin/eva-reporting.conf

    cp ${workspace}/.jboss/guacamole.conf ${jbosshomedir}/bin
    sed -i "s/@JBOSS_HOME@/$JBOSS_HOME_BACKSLACHE/g" ${jbosshomedir}/bin/guacamole.conf

    mkdir -p /etc/jboss-as
    echo "JBOSS_HOME=${jbosshomedir}" > /etc/jboss-as/jboss-as.conf

popd

    # création d'un repertoire /var/log/jboss-as avec les droits pour eva:siveo
        mkdir -p /var/log/jboss-as
        mkdir -p /var/run/jboss-as
        chown -R eva:siveo /var/log/jboss-as
        chown -R eva:root /var/run/jboss-as

   #Modification des droits
       find ${jbosshomedir} -type f -name "*.sh"|xargs -i chmod 750 {}
       find ${jbosshomedir} -type f -name "*.pl"|xargs -i chmod 750 {}
       find ${jbosshomedir} -type f -name "*.ksh"|xargs -i chmod 750 {}

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

       cp $workspace/.guacamole/guacamole.properties $JBOSS_HOME/modules/net/siveo/guacamole/main/properties/guacamole.properties
       sed -i "s/@GUACD_SERVER@/localhost/g" $JBOSS_HOME/modules/net/siveo/guacamole/main/properties/guacamole.properties
       sed -i "s/@GUACD_PORT@/4822/g" $JBOSS_HOME/modules/net/siveo/guacamole/main/properties/guacamole.properties


       chown -R eva:siveo $JBOSS_HOME
       find $JBOSS_HOME|xargs -i chmod 750 {}

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
	sed -i "s/@IPFRONTAL@/${ipFrontal}/g" ${workspace}/.eva/eva.backup.parse


    restart_service postgresql

	# Creation des instances de base eva, activiti, eva-jms + creation du user siveo
	su postgres -c "psql -U postgres -f ${workspace}/.eva/createdb.sql.parse"
	
	# create tables for reporting-quartz instance database
	su postgres -c "psql -U siveo -d reporting-quartz -f ${workspace}/.eva/reporting-quartz.sql"
	
	# Creation des tables de l'instance eva + remplissage des tables
	su postgres -c "psql -U siveo -d eva -f ${workspace}/.eva/eva.backup.parse"
	rm -f ${workspace}/.eva/eva.backup.parse
	
	# Creation des tables de l'instance activiti
	su postgres -c "psql -U siveo -d activiti -f ${workspace}/.eva/eva-activiti.backup"
	
	# Creation des tables de l'instance eva-jms
	su postgres -c "psql -U siveo -d eva-jms -f ${workspace}/.eva/eva-jms.backup"

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

# on verifie l'existence des 2 fichiers
#if [ ! -e $licenseCodeActivationFile -o ! -e $licenseFilePath ]; then
#		return 1
#fi
	
# on change le proprietaire et on affecte le droit 711
mkdir -p /etc/ssl/private
chown -R root:siveo /etc/ssl/private
chmod 711 /etc/ssl/private

licenseCodeActivationFile=/tmp/siveo.sc
licenseFilePath=/tmp/license.details

# on copie le fichier dans /etc/ssl/private/siveo.sc
cp ${licenseCodeActivationFile} ${codeActivationFile}
chmod 600 ${codeActivationFile}
chown eva:siveo ${codeActivationFile}
export CODE_ACTIVATION=$codeActivationFile

# on copie le fichier de détails de license dans $JBOSS_HOME/eva/license
mkdir -p $JBOSS_HOME/eva/license
cp ${licenseFilePath} $JBOSS_HOME/eva/license/license.details
chown eva:siveo ${licenseFilePath}
export LICENSE_DETAILS=$JBOSS_HOME/eva/license/license.details

###### END FIXME

restart_service guacd

#TODO: Before converting configure_postgresql(), be sure that this does not break already installed modules
info_b $"eVA is now configured."
# FIXME: What is the URL for eVA ?
info $"You can access the web interface at https://@HOSTNAME@/eVA/"
