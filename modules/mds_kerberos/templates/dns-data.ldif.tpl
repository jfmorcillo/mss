dn: relativeDomainName=kerberos,ou=@DNSDOMAIN@,ou=@DNSDOMAIN@,ou=DNS,@SUFFIX@
objectClass: top
objectClass: dNSZone
dNSClass: IN
zoneName: @DNSDOMAIN@
cNAMERecord: @HOST@
relativeDomainName: kerberos
structuralObjectClass: dNSZone

dn: relativeDomainName=_kerberos._udp,ou=@DNSDOMAIN@,ou=@DNSDOMAIN@,ou=DNS,@SUFFIX@
objectClass: top
objectClass: dNSZone
dNSClass: IN
zoneName: @DNSDOMAIN@
sRVRecord: 0 0 @KDC_PORT@ @HOST@
relativeDomainName: _kerberos._udp
structuralObjectClass: dNSZone

dn: relativeDomainName=_kerberos-master._udp,ou=@DNSDOMAIN@,ou=@DNSDOMAIN@,ou=DNS,@SUFFIX@
objectClass: top
objectClass: dNSZone
dNSClass: IN
zoneName: @DNSDOMAIN@
sRVRecord: 0 0 @KDC_PORT@ @HOST@
relativeDomainName: _kerberos-master._udp
structuralObjectClass: dNSZone

dn: relativeDomainName=_kerberos-adm._tcp,ou=@DNSDOMAIN@,ou=@DNSDOMAIN@,ou=DNS,@SUFFIX@
objectClass: top
objectClass: dNSZone
dNSClass: IN
zoneName: @DNSDOMAIN@
sRVRecord: 0 0 @KADMIN_PORT@ @HOST@
relativeDomainName: _kerberos-adm._tcp
structuralObjectClass: dNSZone

dn: relativeDomainName=_kpasswd._udp,ou=@DNSDOMAIN@,ou=@DNSDOMAIN@,ou=DNS,@SUFFIX@
objectClass: top
objectClass: dNSZone
dNSClass: IN
zoneName: @DNSDOMAIN@
sRVRecord: 0 0 @KPASSWD_PORT@ @HOST@
relativeDomainName: _kpasswd._udp
structuralObjectClass: dNSZone
