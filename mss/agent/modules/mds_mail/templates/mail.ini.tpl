[main]
disable = 0
# Enable virtual domain support
vDomainSupport = 1
# If vdomain enabled, OU where the domain are stored
vDomainDN = ou=mailDomains, %(baseDN)s
# Enable virtual aliases support
vAliasesSupport = 1
# # If valiases enabled, OU where the aliases are stored
vAliasesDN = ou=mailAliases, %(baseDN)s
# Zarafa support
zarafa = 0

[userdefault]
# For Postfix delivery
# mailbox = %homeDirectory%/Maildir/
# For Dovecot delivery
mailbox = /home/vmail/%uid%/
# Default quota (200 MBytes) set for user
mailuserquota = 204800
