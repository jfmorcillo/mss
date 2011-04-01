Alias /Microsoft-Server-ActiveSync /var/www/z-push/index.php

<Directory "/var/www/z-push/">
    AllowOverride None
    Order allow,deny
    allow from all
    php_flag magic_quotes_gpc off
    php_flag register_globals off
    php_flag magic_quotes_runtime off
    php_flag short_open_tag on
</Directory>
