// secret must be the same as in /etc/rndc.conf
include "/etc/rndc.key";

controls {
    inet 127.0.0.1 port 953
    allow { 127.0.0.1; } keys { mykey; };
};

// Access lists (ACL's) should be defined here
include "/etc/mss_acls.conf";

// Define logging channels
include "/etc/logging.conf";

options {
    version "";
    directory "/var/named";
    dump-file "/var/tmp/named_dump.db";
    pid-file "/var/run/named.pid";
    statistics-file "/var/tmp/named.stats";
    zone-statistics yes;
    coresize 100M; 
    auth-nxdomain yes;
    query-source address * port *;
    listen-on port 53 { any; };
    cleaning-interval 120;
    transfers-in 20;
    transfers-per-ns 2;
    lame-ttl 0;
    max-ncache-ttl 10800;
    include "/etc/mss_forwarders.conf";
    allow-update { none; };
    allow-transfer { none; };
//  allow-query { mss; };
    allow-recursion { mss; };

// Prevent DoS attacks by generating bogus zone transfer 
// requests.  This will result in slower updates to the 
// slave servers (e.g. they will await the poll interval 
// before checking for updates). 

    notify no;

// Generate more efficient zone transfers.  This will place 
// multiple DNS records in a DNS message, instead of one per 
// DNS message. 

    transfer-format many-answers;

// Set the maximum zone transfer time to something more 
// reasonable.  In this case, we state that any zone transfer 
// that takes longer than 60 minutes is unlikely to ever 
// complete.  WARNING:  If you have very large zone files, 
// adjust this to fit your requirements. 

    max-transfer-time-in 60;

// We have no dynamic interfaces, so BIND shouldn't need to 
// poll for interface state {UP|DOWN}. 

    interface-interval 0;

};

include "/var/named/named.conf.ldap";
