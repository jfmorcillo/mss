#!/usr/bin/python
# Copyright Mandriva 2012 all rights reserved

from mss.agent.managers.translation import TranslationManager

_ = TranslationManager().translate

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        domain = sys.argv[1]
        import ldap
        from mmc.plugins.mail import addVDomain, setVDomainDescription
        try:
            addVDomain(domain)
            setVDomainDescription(domain, _("Default mail domain", "mds_mail"))
        except ldap.ALREADY_EXISTS:
            pass
    else:
        print _("Failed to add the mail domain.", "mds_mail")
