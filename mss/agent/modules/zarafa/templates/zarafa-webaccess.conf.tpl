#
# Zarafa Webaccess featuring a 'Look & Feel' similar to Outlook
#

Alias /webaccess /usr/share/zarafa-webaccess/

# Following Apache and PHP settings need to be set to work correct
#
<Directory /usr/share/zarafa-webaccess/>

    Order Allow,Deny
    Allow from All

    # Some apache settings
    Options -Indexes +FollowSymLinks

    # Register globals must be off
    php_flag register_globals off

    # Magic quotes must be off
    php_flag magic_quotes_gpc off
    php_flag magic_quotes_runtime off

    # The maximum POST limit. To upload large files, this value must
    # be larger than upload_max_filesize.
    php_value post_max_size 31M
    php_value upload_max_filesize 30M

    # Short open tags must be on
    php_flag short_open_tag on

    # Uncomment for debugging purposes only. Make sure Apache/PHP can
    # write to this file or no errors will be logged!
#    php_flag log_errors on
#    php_value error_log /var/lib/zarafa-webaccess/error_log
</Directory>
