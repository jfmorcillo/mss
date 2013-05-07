# Copyright Mandriva 2013 all rights reserved
#!/bin/bash

. '../functions.sh'

check_mmc_configured

function randpass() {
    date +%s | sha256sum | base64 | head -c 32
}

owncloud_adminUser=$1
owncloud_adminPass=$2
owncloud_dataPath=$3
OWNCLOUD_TEMPLATE="templates/autoconfig.php.tpl"
OWNCLOUD_AUTOCONFIG="/usr/share/owncloud/config/autoconfig.php"
OWNCLOUD_CONFIG="/usr/share/owncloud/config/config.php"

echo -n "Create ownCloud database..."
dbname="owncloud"
dbuser="owncloud"
dbpass=`randpass 10 1`
mysql_do_query "DROP USER ${dbuser}@'localhost';"
mysql_do_query "DROP DATABASE IF EXISTS ${dbname};"
mysql_do_query "CREATE DATABASE ${dbname};"
mysql_do_query "GRANT ALL ON ${dbname}.* to '${dbuser}'@'localhost' identified by '${dbpass}';"
mysql_do_query "FLUSH PRIVILEGES;"
echo "done."

echo -n "Generating ownCloud configuration..."
[ -e $OWNCLOUD_CONFIG ] && rm -f $OWNCLOUD_CONFIG
cp $OWNCLOUD_TEMPLATE $OWNCLOUD_AUTOCONFIG

[ ! -d $owncloud_dataPath ] && mkdir -p $owncloud_dataPath
chmod 750 $owncloud_dataPath
chown -R apache.apache $owncloud_dataPath

sed -i "s!\@MYSQL_DBNAME\@!$dbname!" $OWNCLOUD_AUTOCONFIG
sed -i "s!\@MYSQL_PASS\@!$dbpass!" $OWNCLOUD_AUTOCONFIG
sed -i "s!\@MYSQL_USER\@!$dbuser!" $OWNCLOUD_AUTOCONFIG
sed -i "s!\@OC_ADMIN\@!$owncloud_adminUser!" $OWNCLOUD_AUTOCONFIG
sed -i "s!\@OC_PASS\@!$owncloud_adminPass!" $OWNCLOUD_AUTOCONFIG
sed -i "s!\@DATA_PATH\@!$owncloud_dataPath!" $OWNCLOUD_AUTOCONFIG
echo "done."

# fullfil the database
echo -n "Filling ownCloud database..."
wget --no-check-certificate -O - http://127.0.0.1/owncloud/ > /dev/null 2>&1

# FIXME: Add a sql request to see if the db has been filled correctly

mysql_do_query "USE owncloud;
                INSERT INTO \`oc_appconfig\` (\`appid\`, \`configkey\`, \`configvalue\`) VALUES
                   ('core', 'backgroundjobs_task', 'OCA\\user_ldap\\lib\\Jobs-updateGroups'),
                   ('user_ldap', 'installed_version', '0.4.0'),
                   ('user_ldap', 'types', 'authentication'),
                   ('user_ldap', 'enabled', 'yes'),
                   ('user_ldap', 'bgjUpdateGroupsLastRun', '1365681892'),
                   ('user_ldap', 'ldap_uuid_attribute', 'auto'),
                   ('user_ldap', 'ldap_host', '127.0.0.1'),
                   ('user_ldap', 'ldap_port', '389'),
                   ('user_ldap', 'ldap_backup_host', ''),
                   ('user_ldap', 'ldap_backup_port', '389'),
                   ('user_ldap', 'ldap_base', '$MDSSUFFIX'),
                   ('user_ldap', 'ldap_base_users', 'ou=People, $MDSSUFFIX'),
                   ('user_ldap', 'ldap_base_groups', 'ou=Group, $MDSSUFFIX'),
                   ('user_ldap', 'ldap_dn', ''),
                   ('user_ldap', 'ldap_agent_password', ''),
                   ('user_ldap', 'ldap_tls', '0'),
                   ('user_ldap', 'ldap_nocase', ''),
                   ('user_ldap', 'ldap_turn_off_cert_check', ''),
                   ('user_ldap', 'ldap_display_name', 'cn'),
                   ('user_ldap', 'ldap_userlist_filter', 'objectClass=inetOrgPerson'),
                   ('user_ldap', 'ldap_group_filter', 'objectClass=posixGroup'),
                   ('user_ldap', 'ldap_group_display_name', 'cn'),
                   ('user_ldap', 'ldap_group_member_assoc_attribute', 'memberUid'),
                   ('user_ldap', 'ldap_login_filter', 'uid=%uid'),
                   ('user_ldap', 'ldap_quota_attr', ''),
                   ('user_ldap', 'ldap_quota_def', ''),
                   ('user_ldap', 'ldap_email_attr', 'mail'),
                   ('user_ldap', 'ldap_cache_ttl', '600'),
                   ('user_ldap', 'ldap_override_main_server', ''),
                   ('user_ldap', 'ldap_configuration_active', '1'),
                   ('user_ldap', 'ldap_attributes_for_user_search', ''),
                   ('user_ldap', 'ldap_attributes_for_group_search', ''),
                   ('user_ldap', 'home_folder_naming_rule', 'homeDirectory');"

mysql_do_query "USE owncloud;
                CREATE TABLE IF NOT EXISTS \`oc_ldap_group_mapping\` (
                    \`ldap_dn\` varchar(255) NOT NULL DEFAULT ' ',
                    \`owncloud_name\` varchar(255) NOT NULL DEFAULT ' ',
                    \`directory_uuid\` varchar(255) NOT NULL DEFAULT ' ',
                    UNIQUE KEY \`ldap_dn_groups\` (\`ldap_dn\`),
                    UNIQUE KEY \`owncloud_name_groups\` (\`owncloud_name\`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"

mysql_do_query "USE owncloud;
                CREATE TABLE IF NOT EXISTS \`oc_ldap_group_members\` (
                    \`owncloudname\` varchar(255) NOT NULL DEFAULT ' ',
                    \`owncloudusers\` longtext NOT NULL,
                    UNIQUE KEY \`ldap_group_members_index\` (\`owncloudname\`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"

mysql_do_query "USE owncloud;
                CREATE TABLE IF NOT EXISTS \`oc_ldap_user_mapping\` (
                    \`ldap_dn\` varchar(255) NOT NULL DEFAULT ' ',
                    \`owncloud_name\` varchar(255) NOT NULL DEFAULT ' ',
                    \`directory_uuid\` varchar(255) NOT NULL DEFAULT ' ',
                    UNIQUE KEY \`ldap_dn_users\` (\`ldap_dn\`),
                    UNIQUE KEY \`owncloud_name_users\` (\`owncloud_name\`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"

echo "done."

https_redirect owncloud /etc/httpd/conf/webapps.d/owncloud.conf

info_b $"ownCloud is now configured."
info $"You can access the web interface at https://@HOSTNAME@/owncloud/"
