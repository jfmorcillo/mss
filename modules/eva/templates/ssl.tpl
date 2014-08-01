NameVirtualHost *:443
<VirtualHost *:443>
        ServerAdmin webmaster@localhost
	SSLEngine On
	SSLCertificateFile /etc/ssl/private/@SSLCERTIFICATFILE@
	SSLCertificateKeyFile /etc/ssl/private/@SSLCERTIFICATKEYFILE@
	#SSLCACertificateFile /etc/ssl/private/thawte-int

        DocumentRoot /var/www/siveo/sites/evplanet-admin/www/
        <Directory /var/www/>
                Options -Indexes -FollowSymLinks MultiViews
                AllowOverride None
                Order allow,deny
                allow from all
        </Directory>

   Alias /evplanet-admin "/var/www/siveo/sites/evplanet-admin/www/"
   <Directory "/var/www/siveo/sites/evplanet-admin/www/">
        Options -Indexes -MultiViews +FollowSymLinks
        AllowOverride None
        Order deny,allow
        Allow from all
    </Directory>

JkMount /siveo-eva/* workerJbossJbpm
JkMount /eva-admin workerJbossAdmin
JkMount /eva-admin/* workerJbossAdmin
JkMount /siveo-reporting-ws/* workerJbossReporting
JKMount /Siveo-vnc-viewer/* workerJbossGuacamole

</VirtualHost>
