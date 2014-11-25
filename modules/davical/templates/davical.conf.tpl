# davical configuration
# DAViCal Calendar Server
Alias /davical /usr/share/davical/htdocs

<Directory /usr/share/davical/htdocs>
  DirectoryIndex index.php index.html
  AllowOverride None
  Require all granted
  AcceptPathInfo On
  php_value include_path /usr/share/php/awl/inc
  php_value magic_quotes_gpc 0
  php_value register_globals 0
  php_value error_reporting "E_ALL & ~E_NOTICE"
  php_value default_charset "utf-8"
  php_admin_flag suhosin.server.strip off
</Directory>

