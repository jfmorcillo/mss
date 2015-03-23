#!/bin/bash
# Copyright Mandriva 2013 all rights reserved

# INCLUDES
. '../functions.sh'

function get_pulse2_interfaces() {
  grep -q 'lan\|wan' /etc/shorewall/interfaces
  if [ $? -eq 0 ]; then
    echo `grep Pulse2Inventory /etc/shorewall/rules | awk '{ print $2 }' | sed -e 's/lan/eth/' -e 's/wan/eth/'`
  fi
}

function get_interface_addr() {
  iface=$1
  echo `ip addr show $iface | grep -o "inet [0-9]*\.[0-9]*\.[0-9]*\.[0-9]*" | sed 's/inet //'`
}

function get_pulse2_zones() {
  grep -q 'lan\|wan' /etc/shorewall/interfaces
  if [ $? -eq 0 ]; then
    echo `grep Pulse2Inventory /etc/shorewall/rules | awk '{ print $2 }'`
  fi
}

function get_interface_addr() {
  iface=$1
  echo `ip addr show $iface | grep -o "inet [0-9]*\.[0-9]*\.[0-9]*\.[0-9]*" | sed 's/inet //'`
}

function configure_imaging() {
    echo "Configuring the time service"
    cat > /etc/xinetd.d/time << EOF
service time
{
   disable        = no
   type           = INTERNAL
   id             = time-stream
   socket_type    = stream
   protocol       = tcp
   user           = root
   wait           = no
}
EOF
    restart_service xinetd

    echo "Configuring the package server for imaging"
    package_srv_conf=/etc/mmc/pulse2/package-server/package-server.ini
    uuid=`uuidgen`
    sed -i 's!^# mount_point!mount_point!' $package_srv_conf
    enable_service pulse2-package-server
    service pulse2-package-server stop
    restart_service pulse2-package-server

    # Enable the imaging plugin
    sed -i 's!^disable.*$!disable = 0!' /etc/mmc/plugins/imaging.ini
    restart_service mmc-agent

    echo "Registering the imaging server"
    mmc_agent_conf=/etc/mmc/agent/config.ini
    mmc_login=`grep '^login' $mmc_agent_conf | sed 's/^.*[[:space:]]\+=[[:space:]]\+//'`
    mmc_password=`grep '^password' $mmc_agent_conf | sed 's/^.*[[:space:]]\+=[[:space:]]\+//'`
    mmc_host=`grep '^host' $mmc_agent_conf | sed 's/^.*[[:space:]]\+=[[:space:]]\+//'`
    mmc_port=`grep '^port' $mmc_agent_conf | sed 's/^.*[[:space:]]\+=[[:space:]]\+//'`
    pulse2-package-server-register-imaging -m https://$mmc_login:$mmc_password@$mmc_host:$mmc_port --check
    if [ $? -eq 0 ]; then
        pulse2-package-server-register-imaging -m https://$mmc_login:$mmc_password@$mmc_host:$mmc_port --name "MBS imaging server"
        [ $? -ne 0 ] && error $"Failed to register the imaging server" && exit 1
    fi

    echo "Associating the imaging server and creating a default boot menu"
    pulse2-load-defaults --default-menu --link-server

    echo "Configuring directories..."
    # Create missing directories
    if [ ! -d /var/lib/pulse2/imaging/bootmenus ]; then
        mkdir /var/lib/pulse2/imaging/bootmenus
    fi
    if [ ! -d /var/lib/pulse2/imaging/isos ]; then
        mkdir /var/lib/pulse2/imaging/isos
    fi

    # Set permissions
    python add_group.py
    chgrp -R Pulse-Admins /var/lib/pulse2/imaging/postinst /var/lib/pulse2/imaging/isos
    chmod -R g+w /var/lib/pulse2/imaging/postinst /var/lib/pulse2/imaging/isos

    # Configure TFTP server
    echo "Configuring TFTP repository..."
    #if [ ! -d /var/lib/tftp/imaging ]; then
    #    mkdir -p /var/lib/tftp/imaging
    #fi
    # Tune fstab if needed
    grep -q 'tftp/imaging' /etc/fstab
    if [ $? -eq 1 ]; then
        echo '' >> /etc/fstab
        echo '# Pulse2 tftp entry' >> /etc/fstab
        #echo '/var/lib/pulse2/imaging  /var/lib/tftp/imaging   none    auto,bind       0 0' >> /etc/fstab
        #mount /var/lib/tftp/imaging
        echo '/var/lib/pulse2/imaging /var/lib/tftp/ none	auto,bind	0 0' >> /etc/fstab
        mount /var/lib/tftp/
    fi

    # Configure NFS share
    echo "Configuring NFS shares..."
    if [ ! -f /etc/exports ]; then
        touch /etc/exports
    fi
    grep -q "pulse2_imaging: configured" /etc/exports
    if [ $? -eq 1 ]; then
        echo "" >> /etc/exports
        echo "# Pulse2 Imaging Exports" >> /etc/exports
        echo "/var/lib/pulse2/imaging/computers 0.0.0.0/0.0.0.0(async,rw,no_root_squash,subtree_check)" >> /etc/exports
        echo "/var/lib/pulse2/imaging/masters 0.0.0.0/0.0.0.0(async,rw,no_root_squash,subtree_check)" >> /etc/exports
        echo "/var/lib/pulse2/imaging/postinst 0.0.0.0/0.0.0.0(async,ro,no_root_squash,subtree_check)" >> /etc/exports
        echo "# pulse2_imaging: configured" >> /etc/exports
        echo "" >> /etc/exports
        restart_service nfs-server
    fi

    # Configure Samba shares if samba is installed
    if [ -f /etc/samba/smb.conf ] && [ -f /usr/sbin/samba ]; then
        echo "Configuring Samba shares..."
        grep -q "pulse2_imaging: configured" /etc/samba/smb.conf
        if [ $? -eq 1 ]; then
            echo "" >> /etc/samba/smb.conf
            echo "[iso]" >> /etc/samba/smb.conf
            echo "  comment = Pulse2 ISO images" >> /etc/samba/smb.conf
            echo "  path = /var/lib/pulse2/imaging/isos" >> /etc/samba/smb.conf
            echo "  browseable = yes" >> /etc/samba/smb.conf
            echo "  writable = yes" >> /etc/samba/smb.conf
            echo "  valid users = @Pulse-Admin" >> /etc/samba/smb.conf
            echo "" >> /etc/samba/smb.conf
            echo "[postinst]" >> /etc/samba/smb.conf
            echo "  comment = Pulse2 Postinstallation files" >> /etc/samba/smb.conf
            echo "  path = /var/lib/pulse2/imaging/postinst" >> /etc/samba/smb.conf
            echo "  browseable = yes" >> /etc/samba/smb.conf
            echo "  writable = yes" >> /etc/samba/smb.conf
            echo "  valid users = @Pulse-Admin" >> /etc/samba/smb.conf
            echo "# pulse2_imaging: configured" >> /etc/samba/smb.conf
            echo "" >> /etc/samba/smb.conf
            restart_service smb
        fi
    fi

    # Regen the agent pack to copy postinstall files
    cp ~/.ssh/id_rsa_pulse.pub /tmp/id_rsa.pub
    /var/lib/pulse2/clients/win32/generate-agent-pack.sh | grep -v '^7zsd.sfx' | grep -v '^7-Zip'
    rm -f /tmp/id_rsa.pub

    enable_service pulse2-package-server
    service pulse2-package-server stop
    restart_service pulse2-package-server
}

function configure_firewall() {
    echo "Firewall configuration..."
    if_name=$1
    if_zone=$2
    if_zone_type=`echo $if_zone | sed 's![0-9]*!!g'`
    # Firewall configuration
    cp -f macro.Pulse2Imaging /etc/shorewall
    mss-add-shorewall-rule -a Pulse2Imaging/ACCEPT -t $if_zone_type
    restart_service shorewall
}

function configure_dhcp() {
    if_name=$1
    if_addr=`get_interface_addr $if_name`
    grep -q "BOOTPROTO=none" /etc/sysconfig/network-scripts/ifcfg-${interface}
    if [ $? -eq 0 ] && [ -n "$if_addr" ]; then
        echo -e "DHCP subnet creation configuration on $ifname..."
        if_netmask=`grep NETMASK= /etc/sysconfig/network-scripts/ifcfg-eth1 | cut -d= -f2`
        # create the DHCP subnet
        python mmc_dhcp.py -i $if_name -a $if_addr -n $if_netmask
        dhcp_configured="$dhcp_configured $if_name"
        restart_service dhcpd
        echo "done"
    else
        echo "No DHCP configuration on $ifname."
        dhcp_external="$dhcp_external $if_name"
    fi
}

check_mmc_configured

TMP_DIR=/var/lib/pulse2/package-server-tmpdir
ENABLE_FUSIONFILE=templates/020_enable_fusioninventory.sh
GLPI_CONFIG=templates/config_db.php
# Retrieve info from filesystem
LDAP_ADMINDN="uid=LDAP Admin,ou=System Accounts,$MDSSUFFIX"

# PARAMETERS
# TODO: Remove and use the password from mysql directly'
myrootpasswd="$1"
fw_lan="$2"
fw_wan="$3"

# We fill the glpi database.
dbname="glpi"
dbuser="glpi"
dbpass=`randpass 10 1`

dhcp_configured=""
dhcp_external=""

ZABBIX_CONF=templates/zabbix.conf.php.tpl


#Configuration of zabbix
echo -n "Create zabbix database..."
zabbixdbname="zabbix"
zabbixdbuser="zabbix"
zabbixdbpass=`randpass 10 1`


if [ ! -e /etc/zabbix/web/ ]; then
	mkdir -p /etc/zabbix/web/
fi

cp $ZABBIX_CONF /etc/zabbix/web/zabbix.conf.php
sed -i "s!\$NAME!$zabbixdbname!" /etc/zabbix/web/zabbix.conf.php
sed -i "s!\$USER!$zabbixdbuser!" /etc/zabbix/web/zabbix.conf.php
sed -i "s!\$PASS!$zabbixdbpass!" /etc/zabbix/web/zabbix.conf.php

mysql_do_query "DROP USER ${zabbixdbuser}@'localhost';"
mysql_do_query "DROP DATABASE IF EXISTS ${zabbixdbname};"
mysql_do_query "CREATE DATABASE ${zabbixdbname};"
mysql_do_query "GRANT ALL ON ${zabbixdbname}.* to '${zabbixdbuser}'@'localhost' identified by '${zabbixdbpass}';"
mysql_do_query "FLUSH PRIVILEGES;"
echo "done."

mysql_password=`cat /root/.my.cnf | grep password  | head -n1 | sed "s/password='\(.*\)'/\1/"`

mysql -uroot -p$mysql_password zabbix < /usr/share/zabbix-mysql/schema.sql
mysql -uroot -p$mysql_password zabbix < /usr/share/zabbix-mysql/images.sql
mysql -uroot -p$mysql_password zabbix < /usr/share/zabbix-mysql/data.sql

mysql_do_query "USE zabbix; UPDATE drules SET status=0 WHERE druleid=2;"
mysql_do_query "USE zabbix; UPDATE hosts SET status=0 WHERE hostid=10084;"
mysql_do_query "USE zabbix; UPDATE actions SET status=0 WHERE actionid=3;"
mysql_do_query "USE zabbix; UPDATE actions SET status=0 WHERE actionid=2;"
mysql_do_query "USE zabbix; UPDATE drules SET iprange=\"127.0.0.1\" WHERE druleid=2;"
mysql_do_query "USE zabbix; UPDATE triggers SET status=1 WHERE triggerid=13083;"
mysql_do_query  "USE zabbix; INSERT INTO groups (groupid, name, internal) VALUES (6, 'Windows', 0), ( 7, 'Apple', 0), ( 8, 'Device', 0);"
mysql_do_query "USE zabbix; INSERT INTO actions (actionid, name, eventsource, evaltype, status, esc_period, def_shortdata, def_longdata, recovery_msg, r_shortdata, r_longdata) VALUES (4, 'Auto discovery. Windows servers.', 1, 0, 0, 0, 'Discovery: {DISCOVERY.DEVICE.STATUS} {DISCOVERY.DEVICE.IPADDRESS}', 'Discovery rule: {DISCOVERY.RULE.NAME}\r\n\r\nDevice IP:{DISCOVERY.DEVICE.IPADDRESS}\r\nDevice DNS: {DISCOVERY.DEVICE.DNS}\r\nDevice status: {DISCOVERY.DEVICE.STATUS}\r\nDevice uptime: {DISCOVERY.DEVICE.UPTIME}\r\n\r\nDevice service name: {DISCOVERY.SERVICE.NAME}\r\nDevice service port: {DISCOVERY.SERVICE.PORT}\r\nDevice service status: {DISCOVERY.SERVICE.STATUS}\r\nDevice service uptime: {DISCOVERY.SERVICE.UPTIME}', 0, '', ''), (5, 'Auto discovery. Mac servers.', 1, 0, 0, 0, 'Discovery: {DISCOVERY.DEVICE.STATUS} {DISCOVERY.DEVICE.IPADDRESS}', 'Discovery rule: {DISCOVERY.RULE.NAME}\r\n\r\nDevice IP:{DISCOVERY.DEVICE.IPADDRESS}\r\nDevice DNS: {DISCOVERY.DEVICE.DNS}\r\nDevice status: {DISCOVERY.DEVICE.STATUS}\r\nDevice uptime: {DISCOVERY.DEVICE.UPTIME}\r\n\r\nDevice service name: {DISCOVERY.SERVICE.NAME}\r\nDevice service port: {DISCOVERY.SERVICE.PORT}\r\nDevice service status: {DISCOVERY.SERVICE.STATUS}\r\nDevice service uptime: {DISCOVERY.SERVICE.UPTIME}', 0, '', '');"
mysql_do_query "USE zabbix; INSERT INTO conditions (conditionid, actionid, conditiontype, operator, value) VALUES (7, 4, 12, 0, 'windows'),(8, 4, 10, 0, '0'),(9, 4, 8, 0, '9'),(10, 5, 12, 0, 'apple'),(11, 5, 10, 0, '0'),(12, 5, 8, 0, '9');"
mysql_do_query "USE zabbix; INSERT INTO operations (operationid, actionid, operationtype, esc_period, esc_step_from, esc_step_to, evaltype) VALUES(4, 2, 2, 0, 1, 1, 0),(5, 5, 2, 0, 1, 1, 0),(6, 5, 4, 0, 1, 1, 0),(7, 5, 6, 0, 1, 1, 0),(8, 4, 2, 0, 1, 1, 0),(9, 4, 4, 0, 1, 1, 0),(10, 4, 6, 0, 1, 1, 0);"
mysql_do_query "USE zabbix; INSERT INTO optemplate (optemplateid, operationid, templateid) VALUES(2, 7, 10050),(3, 7, 10079),(4, 10, 10050),(5, 10, 10081);"
mysql_do_query "USE zabbix; INSERT INTO opgroup (opgroupid, operationid, groupid) VALUES(2, 6, 7),(3, 9, 6);"
mysql_do_query "USE zabbix; INSERT INTO dchecks (dcheckid, druleid, type, key_, snmp_community, ports, snmpv3_securityname, snmpv3_securitylevel, snmpv3_authpassphrase, snmpv3_privpassphrase, uniq) VALUES(3, 2, 12, '', '', '0', '', 0, '', '', 0);"
mysql_do_query "USE zabbix; INSERT INTO rights (rightid, groupid, permission, id) VALUES(15, 8, 2, 7),(16, 8, 2, 8),(17, 8, 2, 5),(18, 8, 2, 2),(19, 8, 2, 1),(20, 8, 2, 6),(21, 8, 2, 4);"



zabbix_api_path="/usr/share/doc/mmc/contrib/monitoring/zabbix-templates"

if [ -e "${zabbix_api_path}/zabbix_api.py.gz" ]; then
	    gunzip -f ${zabbix_api_path}/zabbix_api.py.gz
fi

# Create zabbix autoregistration action
python ${zabbix_api_path}/zabbix_configuration.py --url http://127.0.0.1/zabbix -p ${zabbixdbpass} autoregistration -t "Template App Zabbix Agent"

# add templates
for template in `find ${zabbix_api_path}/templates -type f -name "*.gz"`; do
	gunzip -f ${template}
done

for template in `find ${zabbix_api_path}/templates -type f -name "*.xml" | grep -v "contrib/failed"`; do
	python ${zabbix_api_path}/zabbix_configuration.py --url http://127.0.0.1/zabbix -p ${zabbixdbpass} template ${template}
done


# Tune PHP: increase maximum upload filesize
sed -i 's!^upload_max_filesize = .*$!upload_max_filesize = 150M!' /etc/php.ini
sed -i 's!^post_max_size = .*$!post_max_size = 150M!' /etc/php.ini
restart_service httpd

# Create package directory
mkdir -p $TMP_DIR
chmod 777 $TMP_DIR
chmod o+t $TMP_DIR
sed -i "/src = \/var\/lib\/pulse2\/packages/ {n; s/^tmp_input_dir.*/tmp_input_dir = \/var\/lib\/pulse2\/package-server-tmpdir/}" /etc/mmc/pulse2/package-server/package-server.ini

# Setup the firewall
cp -f macro.Pulse2Inventory /etc/shorewall
[ $fw_lan == "on" ] && mss-add-shorewall-rule -a Pulse2Inventory/ACCEPT -t lan
[ $fw_wan == "on" ] && mss-add-shorewall-rule -a Pulse2Inventory/ACCEPT -t wan

# SSH key management
if [ ! -f /root/.ssh/id_rsa ]; then
	ssh-keygen -t rsa -b 2048 -f /root/.ssh/id_rsa -N '' > /dev/null 2>&1
    [ $? -ne 0 ] && error "Failed to generate a SSH key pair for Pulse2 services" && exit 1
fi
sed -i 's!^.*sshkey_default = .*$!sshkey_default = /root/.ssh/id_rsa!' /etc/mmc/pulse2/launchers/launchers.ini
sed -i "s|/root/.ssh/id_rsa'|/root/.ssh/id_rsa'|" /usr/sbin/pulse2-setup

# Configure inventory module to use GLPI
sed -i 's|# glpi_computer_uri = http://localhost/glpi/front/computer.form.php?id=|glpi_computer_uri = http://localhost/glpi/front/computer.form.php?id=|' /etc/mmc/plugins/glpi.ini
sed -i "s|# glpi_mode = False|glpi_mode = True|" /etc/mmc/pulse2/package-server/package-server.ini
sed -i "s|disable = 1|disable = 0|" /etc/mmc/plugins/glpi.ini

#overwritten by pulse2-setup
#sed -i "s|# enable_forward = False|enable_forward = True|" /etc/mmc/pulse2/inventory-server/inventory-server.ini
#sed -i "s|# url_to_forward = http://localhost/glpi/plugins/fusioninventory/front/plugin_fusioninventory.communication.php|url_to_forward = http://localhost/glpi/plugins/fusioninventory/front/plugin_fusioninventory.communication.php|" /etc/mmc/pulse2/inventory-server/inventory-server.ini

sed -i "s|#purge_machine = 0|purge_machine = 1|" /etc/mmc/plugins/glpi.ini
sed -i "s|#glpi_username = username|glpi_username = glpi|" /etc/mmc/plugins/glpi.ini
sed -i "s|#glpi_password = password|glpi_password = glpi|" /etc/mmc/plugins/glpi.ini
sed -i "s|method = inventory|method = glpi|" /etc/mmc/plugins/base.ini


mysql_get_root_password $myrootpasswd

mysql_do_query "DROP USER ${dbuser}@'localhost';"
mysql_do_query "DROP DATABASE IF EXISTS ${dbname};"
mysql_do_query "CREATE DATABASE ${dbname};"
mysql_do_query "GRANT ALL ON ${dbname}.* to '${dbuser}'@'localhost' identified by '${dbpass}';"
mysql_do_query "FLUSH PRIVILEGES;"

mysql -u $dbuser -p$dbpass $dbname < /usr/share/glpi/install/mysql/glpi-0.84.1-empty.sql

# For security reason we delete the install folder
rm -frv /usr/share/glpi/install

cp  $GLPI_CONFIG /usr/share/glpi/config
sed -i "s/\@DBUSER\@/$dbuser/" /usr/share/glpi/config/config_db.php
sed -i "s/\@DBPASS\@/$dbpass/" /usr/share/glpi/config/config_db.php
sed -i "s/\@DBNAME\@/$dbname/" /usr/share/glpi/config/config_db.php

#Create initial entitie ( if not done pulse2 backtrace )
mysql_do_query "INSERT INTO glpi.glpi_entities (id,entities_id,level,name,completename) VALUES (1,0,1,'glpi','glpi')"

# Enable Fusion inventory plugins
php /usr/share/glpi/plugins/fusioninventory/scripts/cli_install.php &> /dev/null

# Enable fusioninventory
sh $ENABLE_FUSIONFILE

# Check DNS
dig ${FQDN} +nosearch +short | tail -n1 | grep -q -E '([0-9]{1,3}\.){3}[0-9]{1,3}'
is_dns_working=$?
# No DNS try to guess the IP address
if [ ! ${is_dns_working} -eq 0 ]; then
    # Get the first IP address we found
    ifaces=`get_pulse2_interfaces`
    nb_ifaces=`echo $ifaces | wc -w`

    if [ $nb_ifaces -eq 1 ]; then
        FQDN=`get_interface_addr $ifaces`
    elif [ $nb_ifaces -eq 0 ]; then
        error $"You need to allow access to the Pulse2 Inventory server on either internal or external networks."
        exit 1
    elif [ $nb_ifaces -gt 1 ]; then
        error $"A DNS entry must be set for this server if you want the Pulse2 services to listen on multiple interfaces."
        exit 1
    fi
fi
sed -i "s!^public_ip.*!public_ip = ${FQDN}!" /etc/mmc/pulse2/package-server/package-server.ini

# Generate pulse2 agents
cp /root/.ssh/id_rsa.pub /tmp/id_rsa.pub
sed -i 's!/root/.ssh/id_rsa.pub!/tmp/id_rsa.pub!g' /var/lib/pulse2/clients/win32/generate-agent-pack.sh
/var/lib/pulse2/clients/win32/generate-agent-pack.sh | grep -v '^7zsd.sfx' | grep -v '^7-Zip'
rm -f /tmp/id_rsa.pub

# Setup
mkdir -p /var/lib/pulse2/imaging/bootmenus
mkdir -p /var/lib/pulse2/imaging/computers

mysql_password=`cat /root/.my.cnf | grep password  | head -n1 | sed "s/password='\(.*\)'/\1/"`
pulse2-setup -b -R --reset-db \
 --mysql-host=localhost --mysql-user=root --mysql-passwd="$mysql_password" \
 --ldap-uri=ldap://$MDSSERVER/ --ldap-basedn="$MDSSUFFIX" --ldap-admindn="$LDAP_ADMINDN" --ldap-passwd="$MDSPASS" \
 --glpi-enable --glpi-dbhost=localhost --glpi-dbname="glpi" --glpi-dbuser=root --glpi-purge-machines --glpi-dbpasswd="$mysql_password" \
 --glpi-url="localhost/glpi" --zabbix-uri=$MDSSERVER/zabbix --zabbix-user=${zabbixdbuser} --zabbix-password=${zabbixdbpass} \
 | sed -r 's/\x1b.*?[mGKHh]//g'

#sed -i 's!\(glpi_base_url[[:space:]]*=[[:space:]]*http://\)[.[:alnum:]]*\(.*\)!\1localhost\2!' /etc/mmc/plugins/glpi.ini.local

# Disable agent threading
sed -i 's!^multithreading.*$!multithreading = 0!' /etc/mmc/agent/config.ini

# Disable unneeded modules
sed -i 's!^disable.*$!disable = 1!' /etc/mmc/plugins/msc.ini
sed -i 's!^disable.*$!disable = 1!' /etc/mmc/plugins/pkgs.ini
sed -i 's!^disable.*$!disable = 1!' /etc/mmc/plugins/imaging.ini

# Fix external IPs
sed -i "s!^public_ip.*!public_ip = ${FQDN}!" /etc/mmc/pulse2/package-server/package-server.ini
sed -i "s!^tcp_sproxy_host.*!tcp_sproxy_host = ${FQDN}!" /etc/mmc/pulse2/launchers/launchers.ini


# Enable plugins
#sed -i 's!^disable.*$!disable = 0!' /etc/mmc/plugins/msc.ini
#sed -i 's!^disable.*$!disable = 0!' /etc/mmc/plugins/pkgs.ini


#configure_imaging
#zones=`get_pulse2_zones`
#for zone in $zones
#do
#    interface=`echo $zone | sed -e 's/lan/eth/' -e 's/wan/eth/'`
#    configure_firewall $interface $zone
#    configure_dhcp $interface
#done

restart_service mmc-agent

#enable_service pulse2-scheduler
enable_service pulse2-launchers
enable_service pulse2-package-server
service pulse2-scheduler stop
#restart_service pulse2-scheduler
service pulse2-launchers stop
restart_service pulse2-launchers
service pulse2-package-server stop
restart_service pulse2-package-server

# Setup the firewall
cp -f macro.Pulse2Deployment /etc/shorewall
network=`grep Pulse2Inventory /etc/shorewall/rules | head -n1 | awk '{ print $2 }' | sed 's/[0-9]$//'`
mss-add-shorewall-rule -a Pulse2Deployment/ACCEPT -t $network
restart_service shorewall

restart_service mmc-agent

# INFORMATION
info_b $"Pulse2 module is installed and configured."
info $"The module is available on the management interface at https://@HOSTNAME@/mmc/."
info $"Check the documentation to use Pulse2 features."
for interface in $dhcp_configured
do
    info $"- DHCP subnet configured on $interface for Pulse2 imaging clients."
done
for interface in $dhcp_external
do
    info $"- The external DHCP server used on $interface must be configured for Pulse2."
done
info $"Check the documentation to use the Pulse2 imaging at http://serviceplace.mandriva.com/addons/mbs/1.0/pulse2_imaging/."

exit 0
