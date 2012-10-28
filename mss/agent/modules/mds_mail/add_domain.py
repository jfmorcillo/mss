#!/usr/bin/python
# Copyright Mandriva 2012 all rights reserved

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        domain = sys.argv[1]
        import ldap
        from mmc.plugins.mail import addVDomain, setVDomainDescription
        try:
            addVDomain(domain)
            setVDomainDescription(domain, "Default mail domain")
        except ldap.ALREADY_EXISTS:
            pass
    else:
        print "Failed to add the mail domain."
