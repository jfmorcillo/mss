[main]
disable = 0
# Enable virtual domain support
vDomainSupport = 1
# If vdomain enabled, OU where the domain are stored
vDomainDN = ou=mailDomains,@SUFFIX@
zarafa = 1

[userdefault]
# For Postfix delivery
# mailbox = %homeDirectory%/Maildir/
# For Dovecot delivery
mailbox = /home/vmail/%uid%/
# Default quota (200 MBytes) set for user
mailuserquota = 204800
