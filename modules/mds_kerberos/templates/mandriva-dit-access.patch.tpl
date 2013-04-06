153a154,170
> # Kerberos
> access to dn.subtree="ou=kerberos,@SUFFIX@"
> 	attrs=entry
>  	by group.exact="cn=Kerberos Readers,ou=System Groups,@SUFFIX@" read
>  	by group.exact="cn=Kerberos Admins,ou=System Groups,@SUFFIX@" write
>  	by * read
> 
> access to dn.subtree="ou=kerberos,@SUFFIX@"
>  	by group.exact="cn=Kerberos Readers,ou=System Groups,@SUFFIX@" read
>  	by group.exact="cn=Kerberos Admins,ou=System Groups,@SUFFIX@" write
>  	by * search
>  
> access to dn.subtree="cn=@REALM@,ou=kerberos,@SUFFIX@"
>  	by group.exact="cn=Kerberos Readers,ou=System Groups,@SUFFIX@" read
>  	by group.exact="cn=Kerberos Admins,ou=System Groups,@SUFFIX@" write
>  	by * none
>  

