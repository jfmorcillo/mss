dn:relativeDomainName=kerberos,ou=@DNSDOMAIN@,ou=@DNSDOMAIN@,ou=DNS,@SUFFIX@
changetype:modify
replace:zoneName
zoneName:@DNSDOMAIN@
-
replace:cNAMERecord
cNAMERecord:@HOST@
-

dn:relativeDomainName=_kerberos._udp,ou=@DNSDOMAIN@,ou=@DNSDOMAIN@,ou=DNS,@SUFFIX@
changetype:modify
replace:zoneName
zoneName:@DNSDOMAIN@
-
replace:sRVRecord
sRVRecord: 0 0 @KDC_PORT@ @HOST@
-

dn:relativeDomainName=_kerberos-master._udp,ou=@DNSDOMAIN@,ou=@DNSDOMAIN@,ou=DNS,@SUFFIX@
changetype:modify
replace:zoneName
zoneName:@DNSDOMAIN@
-
replace:sRVRecord
sRVRecord: 0 0 @KDC_PORT@ @HOST@
-

dn:relativeDomainName=_kerberos-adm._tcp,ou=@DNSDOMAIN@,ou=@DNSDOMAIN@,ou=DNS,@SUFFIX@
changetype:modify
replace:zoneName
zoneName:@DNSDOMAIN@
-
replace:sRVRecord
sRVRecord: 0 0 @KADMIN_PORT@ @HOST@
-

dn:relativeDomainName=_kpasswd._udp,ou=@DNSDOMAIN@,ou=@DNSDOMAIN@,ou=DNS,@SUFFIX@
changetype:modify
replace:zoneName
zoneName:@DNSDOMAIN@
-
replace:sRVRecord
sRVRecord: 0 0 @KPASSWD_PORT@ @HOST@
-
