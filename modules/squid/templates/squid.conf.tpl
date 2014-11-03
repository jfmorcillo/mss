hierarchy_stoplist cgi-bin ?
acl QUERY urlpath_regex cgi-bin \?
no_cache deny QUERY
dns_nameservers localhost
maximum_object_size_in_memory 64 KB
cache_store_log none
hosts_file /etc/hosts

#### AUTH CONF
auth_param basic realm Proxy authentication
auth_param basic program /usr/lib64/squid/basic_ldap_auth -b "@SUFFIX@" -f uid=%s localhost
auth_param basic children 5
auth_param basic casesensitive off
auth_param basic credentialsttl 2 hours

external_acl_type ldap_group %LOGIN /usr/lib64/squid/ext_ldap_group_acl -d -b "@SUFFIX@" -f "(&(memberuid=%u)(cn=%g))" -h localhost
####

acl localhost src 127.0.0.1/32 ::1
acl to_localhost dst 127.0.0.0/8 0.0.0.0/32 ::1

acl SSL_ports port 443
acl Safe_ports port 80          # http
acl Safe_ports port 21          # ftp
acl Safe_ports port 443         # https
acl Safe_ports port 70          # gopher
acl Safe_ports port 210         # wais
acl Safe_ports port 1025-65535  # unregistered ports
acl Safe_ports port 280         # http-mgmt
acl Safe_ports port 488         # gss-http
acl Safe_ports port 591         # filemaker
acl Safe_ports port 777         # multiling http
acl CONNECT method CONNECT

acl auth proxy_auth REQUIRED

acl filtered_group external ldap_group InternetFiltered
acl nonfiltered_group external ldap_group InternetMaster

acl blacklist url_regex -i "/etc/squid/rules/blacklist.txt"
acl blacklist_ext urlpath_regex -i "/etc/squid/rules/blacklist_ext.txt"
acl whitelist url_regex -i "/etc/squid/rules/whitelist.txt"
acl timeranges time MTWHF "/etc/squid/rules/timeranges.txt"
acl machines src "/etc/squid/rules/machines.txt"

##############################################################################
http_access allow manager localhost
http_access deny manager

http_access deny !Safe_ports
http_access deny CONNECT !SSL_ports

# Permissions: Block and Allow? not remove #Allow and #Deny they are marks.
#Allow
http_access allow nonfiltered_group all
http_access deny all filtered_group blacklist_ext
http_access allow all filtered_group timeranges
http_access deny filtered_group blacklist
http_access allow filtered_group whitelist
http_access allow filtered_group all
http_access allow machines all

#Deny
http_access deny all

#################################################################################

http_port 3128

# Uncomment and adjust the following to add a disk cache directory.
cache_dir ufs /var/spool/squid 500 16 256

# Leave coredumps in the first cache dir
coredump_dir /var/spool/squid

# Add any of your own refresh_pattern entries above these.
refresh_pattern ^ftp:           1440    20%     10080
refresh_pattern ^gopher:        1440    0%      1440
refresh_pattern -i (/cgi-bin/|\?) 0     0%      0
refresh_pattern .               0       20%     4320
refresh_pattern -i \.(mp3|mp4|m4a|ogg|mov|avi|wmv)$ 10080 90% 999999 ignore-no-cache override-expire ignore-private
