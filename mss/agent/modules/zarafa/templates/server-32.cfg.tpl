##############################################################

# SERVER SETTINGS



# IP Address to bind to (0.0.0.0 for ANY)

# Set to 127.0.0.1 if connections should only come from localhost

# and through the webserver proxy

server_bind		= 0.0.0.0



# Accept normal TCP connections (not recommended to disable)

server_tcp_enabled	= yes



# Port to bind to

server_tcp_port		= 236



# Accept unix pipe connections (not recommended to disable)

server_pipe_enabled	= yes



# Unix socket location

server_pipe_name	= /var/run/zarafa



# Database engine (mysql)

database_engine		= mysql



# Allow connections from normal users through the unix socket

allow_local_users	= yes



# local admin users who can connect to any store (use this for the zarafa-dagent)

# field is SPACE separated

local_admin_users	= root zarafa



# e-mail address of the Zarafa System user

system_email_address	= postmaster



# drop privileges and run the process as this user

run_as_user		= zarafa



# drop privileges and run the process as this group

run_as_group		= zarafa



# create a pid file for stopping the service via the init.d scripts

pid_file		= /var/run/zarafa-server.pid



# run server in this path (when not using the -F switch)

running_path = /



# session timeout for clients. Values lower than 300 will be upped to 300

# automatically. If the server hears nothing from a client in session_timeout

# seconds, then the session is killed.

session_timeout		= 300



# Socket to connect to for license server

license_socket		= /var/run/zarafa-licensed



##############################################################

# LOG SETTINGS



# Logging method (syslog, eventlog, file)

log_method		= file


# Logfile (for log_method = file
log_file		= /var/log/zarafa/server.log


# Loglevel (0=no logging, 5=full logging)

log_level		= 5



# Log timestamp - prefix each log line with timestamp in 'file' logging mode

log_timestamp		= 1



##############################################################

# MYSQL SETTINGS (for database_engine = mysql)



# MySQL hostname to connect to for database access

mysql_host		= localhost


# MySQL port to connect with (usually 3306)

mysql_port		= 3306


# The user under which we connect with MySQL

mysql_user		= zarafa


# The password for the user (leave empty for no password)

mysql_password		= @MYSQLPASSWORD@


# Database to connect to

mysql_database		= zarafa


# Where to place attachments. Value can be 'database' or 'files'

attachment_storage	= files



# When attachment_storage is 'files', use this path to store the files

attachment_path		= @ATTACHMENTSPATH@



##############################################################

#  SSL SETTINGS



# enable SSL support in server

server_ssl_enabled	= no



# Listen for SSL connections on this port

server_ssl_port		= 237



# Required Server certificate, contains the certificate and the private key parts

server_ssl_key_file	= /etc/zarafa/ssl/server.pem



# Password of Server certificate

server_ssl_key_pass	= replace-with-server-cert-password



# Required Certificate Authority of server

server_ssl_ca_file	= /etc/zarafa/ssl/cacert.pem



# Path with CA certificates, e.g. /etc/ssl/certs

server_ssl_ca_path	=



# Path of SSL Public keys of clients

sslkeys_path		= /etc/zarafa/sslkeys





##############################################################

#  OTHER SETTINGS



# Softdelete clean cycle (in days) 0=never running

softdelete_lifetime	= 30



# Sync lifetime, removes all changes remembered for a client after x days of inactivity

sync_lifetime		= 365



# Set to 'yes' if all changes (for synchronization) to messages should be logged to the database

sync_log_all_changes = no


#############################################################

# CACHE SETTINGS



# Size in bytes of the 'cell' cache (should be set as high as you can afford to set it)

cache_cell_size			= 16777216



# Size in bytes of the 'object' cache

cache_object_size		= 5242880



# Size in bytes of the 'indexed object' cache

cache_indexedobject_size	= 16777216



# Lifetime for userquota details

cache_quota_lifetime		= 1



# Lifetime for user details

cache_userdetails_lifetime	= 5



##############################################################

#  QUOTA SETTINGS



# The default Warning Quota Level. Set to 0 to disable this level.

# The user will receive an email when this level is reached. Value is in Mb. Default value is 0.

quota_warn		= 0



# The default Soft Quota Level. Set to 0 to disable this level.

# The user will still receive mail, but sending new mail is prohibited, until objects are removed from the store.

# VALUE is in Mb. Default value is 0.

quota_soft		= 0



# The default Hard Quota Level. Set to 0 to disable this level.

# The user can not receive and send mail, until objects are removed from the store.

# Value is in Mb. Default value is 0.

quota_hard		= 0



# The default Warning Quota Level. Set to 0 to disable this level.

# The company administrator will receive an email when this level is reached. Value is in Mb. Default value is 0.

companyquota_warn      = 0



##############################################################

#  USER PLUGIN SETTINGS



# Name of the plugin that handles users

# Required, default = ldap

# Values: ldap, unix, db

user_plugin		= ldap



# configuration file of the user plugin, examples can be found in /usr/share/zarafa/example-config

user_plugin_config	= /etc/zarafa/ldap.cfg



# location of the zarafa plugins

# if you have a 64bit distribution, this probably should be changed to /usr/lib64/zarafa

plugin_path		= /usr/lib/zarafa



# scripts which create stores for users from an external source

# used for ldap and unix plugins only

createuser_script	= /etc/zarafa/userscripts/createuser
deleteuser_script	= /etc/zarafa/userscripts/deleteuser
creategroup_script	= /etc/zarafa/userscripts/creategroup
deletegroup_script	= /etc/zarafa/userscripts/deletegroup
createcompany_script	= /etc/zarafa/userscripts/createcompany
deletecompany_script	= /etc/zarafa/userscripts/deletecompany

##############################################################

# MISC SETTINGS



# Enable multi-company environment

# When set to true it is possible to create companies within the

# zarafa instance and assign all users and groups to particular

# companies.

# When set to false, the normal single-company environment is created.

enable_hosted_zarafa = false



# Display format of store name

# Allowed variables:

#  %u Username

#  %f Fullname

#  %c Companyname

# default: %f

storename_format = %f



# Loginname format (for Hosted installations)

# When the user does not login through a system-wide unique

# username (like the email address) a unique name is created

# by combining the username and the companyname.

# With this configuration option you can set how the

# loginname should be built up.

#

# Allowed variables:

#  %u username

#  %c companyname

#

# default: %u

loginname_format = %u

