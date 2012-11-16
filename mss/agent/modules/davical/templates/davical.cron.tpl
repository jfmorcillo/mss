# syncs davical user list with the ldap user list
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m h dom mon dow user  command
08 *    * * *   apache /usr/bin/php --define 'error_reporting = E_ALL & ~E_DEPRECATED & ~E_NOTICE' /usr/share/davical/scripts/cron-sync-ldap.php @FQDN@
#