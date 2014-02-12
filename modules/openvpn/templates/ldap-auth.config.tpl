<LDAP>
        # LDAP server URL
        URL             ldap://127.0.0.1:389

        # Bind DN (If your LDAP server doesn't support anonymous binds)
        #BindDN          "CN=MyReadOnlyUser,@MDSSUFFIX@"

        # Bind Password
        #Password        "MyReadOnlyUserPassword"

        # Network timeout (in seconds)
        Timeout         15

        # Enable Start TLS
        TLSEnable       no

        # Follow LDAP Referrals (anonymously)
        FollowReferrals no

        # TLS CA Certificate File
        TLSCACertFile   /etc/ssl/ca.pem

        # TLS CA Certificate Directory
        TLSCACertDir    /etc/ssl/certs

        # Client Certificate and key
        # If TLS client authentication is required
        TLSCertFile     /etc/ssl/client-cert.pem
        TLSKeyFile      /etc/ssl/client-key.pem

        # Cipher Suite
        # The defaults are usually fine here
        # TLSCipherSuite        ALL:!ADH:@STRENGTH
</LDAP>

<Authorization>
        # Base DN
        BaseDN          "ou=People,@MDSSUFFIX@"

        # User Search Filter
        SearchFilter   "(&(uid=%u))"
        #SearchFilter   "(&(sAMAccountName=%u)(msNPAllowDialin=TRUE))"
        #SearchFilter    "(&(sAMAccountName=%u))"

        # Require Group Membership
        RequireGroup    true

        # Add non-group members to a PF table (disabled)
        #PFTable        ips_vpn_users

        <Group>
                RFC2307bis      false
                BaseDN          "@MDSSUFFIX@"
                SearchFilter    "(cn=VPNUsers)"
                MemberAttribute "memberUid"
                # Add group members to a PF table (disabled)
                #PFTable        ips_vpn_eng
        </Group>
</Authorization>
