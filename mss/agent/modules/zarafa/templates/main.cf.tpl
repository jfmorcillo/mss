smtpd_banner = $myhostname ESMTP $mail_name (Mandriva MES5)
biff = no

# appending .domain is the MUA's job.
append_at_myorigin = yes
append_dot_mydomain = no

myhostname = @FQDN@
alias_maps = hash:/etc/postfix/aliases
alias_database = hash:/etc/postfix/aliases
myorigin = @FQDN@
mydestination = @FQDN@, @HOSTNAME@, localhost.localdomain, localhost
relayhost = 
mynetworks = @MYNETWORKS@
mailbox_size_limit = 0
recipient_delimiter = +
inet_interfaces = all
luser_relay = 

delay_warning_time = 4h 
maximal_queue_lifetime = 10d 
mailbox_size_limit = 0 
message_size_limit = 15728640

# LDAP Transport 
transport_map = ldap:/etc/postfix/ldap-transport.cf 

# Virtual Domains Control
virtual_mailbox_domains = ldap:/etc/postfix/ldap-domains.cf
virtual_mailbox_maps = ldap:/etc/postfix/ldap-accounts.cf
virtual_mailbox_base = 
virtual_alias_maps = ldap:/etc/postfix/ldap-aliases.cf, ldap:/etc/postfix/ldap-maildrop.cf
virtual_alias_domains =
virtual_minimum_uid = 100
virtual_uid_maps = static:vmail 
virtual_gid_maps = static:mail

# Zarafa LDA 
virtual_transport = lmtp:127.0.0.1:2003
zarafa_destination_recipient_limit = 1

# TLS parameters
smtpd_use_tls = yes
smtpd_tls_loglevel = 1
smtpd_tls_cert_file = /etc/mss/ssl/smtpd.pem 
smtpd_tls_key_file = /etc/mss/ssl/smtpd.key

# Wait until the RCPT TO command before evaluating restrictions 
smtpd_delay_reject = yes 

# Basics Restrictions 
smtpd_helo_required = yes 
strict_rfc821_envelopes = yes 

content_filter = amavis:[127.0.0.1]:10025

smtpd_recipient_restrictions =
    permit_mynetworks,
    reject_non_fqdn_recipient,
    reject_unknown_recipient_domain,
    reject_unauth_destination,
    permit

smtpd_helo_restrictions =
    permit_mynetworks,
    # outlook clients limits
    # reject_non_fqdn_hostname,
    # reject_invalid_hostname,
    permit

smtpd_sender_restrictions =
    permit_mynetworks,
    reject_non_fqdn_sender,
    reject_unknown_sender_domain,
    permit

smtpd_client_restrictions =
    permit_mynetworks,
    reject_rbl_client bl.spamcop.net, 
    reject_rbl_client dnsbl.njabl.org, 
    reject_rbl_client cbl.abuseat.org, 
    reject_rbl_client sbl-xbl.spamhaus.org, 
    permit

smtpd_data_restrictions =
    reject_unauth_pipelining,
    permit

