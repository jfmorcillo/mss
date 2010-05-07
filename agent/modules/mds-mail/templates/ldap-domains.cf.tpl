server_host = @HOST@
server_port = 389
search_base = ou=mailDomains,@SUFFIX@
query_filter = (&(objectClass=mailDomain)(virtualdomain=%s))
result_attribute = virtualdomain
version = 3
