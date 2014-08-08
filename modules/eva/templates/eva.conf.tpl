RedirectMatch ^/$ /eva-first-run/
DocumentRoot /var/www/siveo/sites/evplanet-admin/www/
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
