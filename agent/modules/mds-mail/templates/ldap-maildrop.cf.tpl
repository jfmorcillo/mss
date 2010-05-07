server_host = @HOST@
server_port = 389
search_base = ou=People,@SUFFIX@
query_filter = (&(objectClass=mailAccount)(mailenable=OK)(mail=%s))
result_attribute = maildrop
version = 3
