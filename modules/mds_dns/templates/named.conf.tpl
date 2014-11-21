// Access lists (ACL's) should be defined here
include "/etc/mss_acls.conf";

options {
    listen-on port 53 { any; };
    listen-on-v6 port 53 { any; };
    directory "/var/named";
    dump-file "/var/named/data/cache_dump.db";
    statistics-file "/var/named/data/named_stats.txt";
    memstatistics-file "/var/named/data/named_mem_stats.txt";
    pid-file "/var/run/named.pid";

    dnssec-enable no;
    dnssec-validation no;
    dnssec-lookaside auto;

    /* Path to ISC DLV key */
    bindkeys-file "/etc/named.iscdlv.key";

    managed-keys-directory "/var/named/dynamic";

    zone-statistics yes;
    coresize 100M;
    auth-nxdomain yes;
    query-source address * port *;
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

logging {
        channel default_debug {
                file "data/named.run";
                severity dynamic;
        };
};

include "/etc/named.root.key";

zone "." IN {
    type hint;
    file "named.ca";
};

zone "localhost.localdomain" IN {
    type master;
    file "named.localhost";
    allow-update { none; };
};

zone "localhost" IN {
    type master;
    file "named.localhost";
    allow-update { none; };
};

zone "1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.ip6.arpa" IN {
    type master;
    file "named.loopback";
    allow-update { none; };
};

zone "1.0.0.127.in-addr.arpa" IN {
    type master;
    file "named.loopback";
    allow-update { none; };
};

zone "0.in-addr.arpa" IN {
    type master;
    file "named.empty";
    allow-update { none; };
};

include "/var/named/named.conf.ldap";
