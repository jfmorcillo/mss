[ldap]
host = 127.0.0.1
baseDN = @SUFFIX@
baseUsersDN = ou=People, @SUFFIX@
baseGroupsDN = ou=Group, @SUFFIX@
rootName = uid=LDAP Admin,ou=System Accounts,@SUFFIX@
password = @PASSWORD@
userHomeAction = 1
skelDir = /etc/skel
defaultUserGroup = users
defaultHomeDir = /home
uidStart = 10000
gidStart = 10000
# deprecated logview module
logViewModule = no
logfile = /var/log/ldap/ldap.log
passwordscheme = passmod
authorizedHomeDir = /home

[backup-tools]
path = /usr/lib/mmc/backup-tools
destpath = /home/archives

# Subscription informations
[subscription]
product_name = Mandriva Business Server Soho
vendor_name = Mandriva
vendor_mail = sales@mandriva.com
# customer_name =
# customer_mail =
# comment =
users = 5
# computers = 0
upgrade_url =
# Support informations
support_mail =
support_phone =
support_comment =
