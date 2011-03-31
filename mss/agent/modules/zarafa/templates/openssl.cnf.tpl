[ req ] 
default_bits            = 2048 
default_keyfile         = privkey.pem 
distinguished_name      = req_distinguished_name 
prompt                  = no 
string_mask             = nombstr 
x509_extensions         = server_cert 
 
[ req_distinguished_name ] 
countryName             = FR
stateOrProvinceName     = France
localityName            = Paris
organizationName        = Mandriva
organizationalUnitName  = SMTP Server 
commonName              = @COMMONNAME@
emailAddress            = postmaster@@DOMAIN@
 
[ server_cert ] 
basicConstraints        = critical, CA:FALSE 
subjectKeyIdentifier    = hash 
keyUsage                = digitalSignature, keyEncipherment 
extendedKeyUsage        = serverAuth, clientAuth 
nsCertType              = server 
nsComment               = "SMTP Server"
