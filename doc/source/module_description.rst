Module description
=================================================

The stock modules are located in the modules directory.

Each module directory contains:

- a JSON file describing the module, ``desc.json``
- an ``__init__.py`` file because a module is also a python module
- some python functions to retrieve the current configuration in the ``__init__.py`` file (optional)
- gettext files
- a setup script (optional)
- templates files used by the setup script (optional)

The desc.json file
-------------------------------------------------

For full examples of the ``desc.json`` file check-out the :doc:`module_desc_example` page.

.. highlight:: javascript

Basic description
^^^^^^^^^^^^^^^^^
The module is identified by its slug. Basically it uses the same name of the
module's directory.

::

 {
    "slug": "module1",
    "name": "My module",
    "description": "A great module",


Categorization and location
^^^^^^^^^^^^^^^^^^^^^^^^^^^

For the module to appear in the web client you need to set it's section and
optionnaly a category in this section.

::

    "standalone": true,
    "categories": [
        {
            "slug": "users",
            "name": "Users"
        }
    ],
    "module": {
        "section": "core"
    }

Sections are defined in ``modules/sections.json``.

The module can be hidden when using standalone = false.

Actions
^^^^^^^

Action menu to display when the module has been configured. Currently only
html links are supported.

::

    "actions": [
        {
            "type": "link",
            "name": "Management interface",
            "value": "https://@HOSTNAME@/mmc/main.php"
        },
        {
            "type": "link",
            "name": "Webmail interface",
            "value": "http://@HOSTNAME@/roundcubemail/"
        }
    ],

Repositories
^^^^^^^^^^^^

MSS allows you to add repositories on the system to install packages.

* @slug: name used in the urmpi.cfg file
* @name: name displayed in the web interface when adding the repository
* @url: location of the repository
* @restricted: if repository need an HTTP authentication
* @options: options passed to the package manager when adding the media

@ARCH@ will be replaced by the machine arch (x86_64 or i586).

::

    "repositories": [
        {
            "slug": "repo1",
            "name": "Repository one",
            "url": "http://mirror.mandriva.com/one/@ARCH@/",
            "restricted": false,
            "options": "--updates"
        },
        {
            "slug": "repo2",
            "name": "Repository two",
            "url": "http://mirror.mandriva.com/two/@ARCH@/",
            "restricted": true,
            "options": "--distrib"
        }
    ]


Packages
^^^^^^^^

Your module may install some packages. The packages can be arch dependant.

* @name: i586 | x86_64 | all

::

    "packages": [
        {
            "name": "all",
            "rpms": [
                "openldap-servers",
                "openldap-clients"
            ]
        },
        {
            "name": "i686",
            "rpms": [
                "libsasl2-plug-gssapi"
            ]
        },
        {
            "name": "x86_64",
            "rpms": [
                "lib64sasl2-plug-gssapi"
            ]
        }
    ]

Conflicts
^^^^^^^^^

If the module conflicts with other modules in MSS.

::

    "module": {
        "conflicts": ["module2"]
    }


Dependencies
^^^^^^^^^^^^

You can add dependencies with other modules. If some module is added as a
dependency it will be installed and configured before the current module.

::

    "module": {
        "dependencies": ["module34", "module23"]
    }

Module configuration
^^^^^^^^^^^^^^^^^^^^

The module configuration may need some information provided by the user. Several
field can be used to gather the information needed to run a configuration script.

Configuration definition starts with :

::

    "config": [

Then add some form fields.

Simple text field
"""""""""""""""""

* @name: field name
* @require: the field is mandatory (optional)
* @default: default value for the field - can be a string or a custom method (optional)
* @validation: fqdn | ip | custom method (validate the field data - optional)
* @label: verbose name of the field
* @help: verbose help for the field

::

    {
        "type": "text",
        "name": "server1",
        "label": "Server 1 IP",
        "help": "The first server IP address",
        "require": "yes",
        "default": "127.0.0.1",
        "validation": "ip"
    }


The custom method for validation or the default value must be declared in the
module's __init__.py file.

Password field
""""""""""""""

The generated form will add automatically a second password field to validate
the password in the web client.

* @name: field name
* @require: the field is mandatory (optional)
* @default: default value for the field - can be a string or a custom method (optional)


::

        {
            "type": "password",
            "name": "passwd",
            "label": "Password",
            "help": "The server password",
            "require": "yes",
            "default": ""
        }

Multi text field
""""""""""""""""

Same as a text field but with the multi option. Will allow the user to specify
multiple value for this field.

::

        {
            "type": "text",
            "multi": "yes",
            "name": "param1",
            ...
        }

Network field
"""""""""""""

This special field let the user input a network description (ip/netmask)

* @name: field name
* @format: long | short (/24 or /255.255.255.0 - format used in the config script)
* @default: default value for the field - can be a string or a custom method (optional)
* @validation: network (optional)


::

        {
            "type": "network",
            "name": "bind_networks",
            "format": "short",
            "validation": "network",
            "default": "get_networks",
            "label": "My networks",
            "help": "Specify which networks are authorized to resolve external queries with your DNS server (recursion). eg: 192.168.0.0/255.255.255.0."
        }

Select list field
"""""""""""""""""

* @name: field name
* @require: yes | no
* @options: list of values

::

        {
            "type": "options",
            "name": "popimap_proto",
            "require": "yes",
            "label": "Protocols supported",
            "help": "Protocols that the dovecot server will provide.",
            "options": [
                        { "name": "IMAPS and POP3S", "value": "imap imaps pop3 pop3s" },
                        { "name": "IMAPS", "value": "imaps imap" },
                        { "name": "POP3S", "value": "pop3s pop3" }
            ]
        }

Checkbox field
""""""""""""""

* @name: field name
* @default: on | off

::

        {
            "type": "check",
            "name": "fw_lan",
            "default": "on",
            "label": "Allow mail services access from internal networks",
            "help": "Configure the firewall to accept smtp/imap/pop3 connections on interfaces configured as 'internal'"
        }

For full examples of the ``desc.json`` file check-out the :doc:`module_desc_example` page.


The __init__.py file
-------------------------------------------------

Because a MSS module is also a python module, a ``__init__.py`` must be created. This
file may contain two python functions related to the module configuration.

If the module has a configuration script, the function :py:func:`get_config_info` has
to be declared.

.. py:function:: get_config_info()

    Returns module script name and parameters

    :rtype: tuple ("script name", ["list", "of", "params"])


MSS use this function to get the name of the configuration script and the order
of the parameters used to call the script. The script name is relative to the
module directory. The names of the parameters are the field names used in the
configuration description in ``desc.json``.

If you want to retrieve the current configuration of the module when configuring
the module you have to write a :py:func:`get_current_config` function.

.. py:function:: get_current_config()

    Returns current configuration of the module

    :rtype: dict { "param1": value, "param2": value, ... }


The values returned by this function replaces the default values set in in the
configuration description in ``desc.json``. Have a look in ``mds_*`` modules for some examples.

After a module is configured on MSS, the module is automatically tagged as
configured in the MSS database. You can also write a :py:func:`check_configured`
function that tells MSS if the module is configured or not. This will override
the database value.

.. py:function:: check_configured()

    Returns module's configuration state

    :rtype: bool


Dynamic configuration fields
----------------------------

If you want to generate configuration fields dynamically you can create a
custom field in ``desc.json``:

::

    "config": [
        {
            "type": "custom",
            "name": "interfaces"
        }
    ]

Then in ``__init__.py`` write the ``get_<field_name>_config`` function to return
the fields definition in python. A good example is in the network module. The
method will create configuration fields for all network interfaces available on
the host.


Example of ``mds_mmc`` module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Configuration definition in ``desc.json`` :

::

    "config": [
        {
            "type": "password",
            "name": "mdspasswd",
            "require": "yes",
            "label": "Administrator password",
            "help": "The administrator password of the web interface for managing MBS users and services."
        },
        {
            "type": "check",
            "name": "fw_lan",
            "default": "on",
            "label": "Allow access from internal networks",
            "help": "Configure the firewall to allow access to the web interface from internal networks"
        },
        {
            "type": "check",
            "name": "fw_wan",
            "default": "off",
            "label": "Allow access from external networks",
            "help": "Configure the firewall to allow access to the web interface from external networks"
        }
    ],


``__init__.py`` file :

.. literalinclude:: ../../modules/mds_mmc/__init__.py
    :linenos:
    :language: py

The setup script and templates
------------------------------

To run modules configuration the MSS agent runs shell scripts as root in the
background. The script name and its parameters launch by MSS have to be declared
in the :py:func:`get_config_info` function.

``mds_webmail`` script example :

.. literalinclude:: ../../modules/mds_webmail/setup-webmail.sh
    :linenos:
    :language: sh

Script templates
^^^^^^^^^^^^^^^^

The setup script may use some configuration file templates which are located in
a ``templates`` directory in the module's directory.

Script output
^^^^^^^^^^^^^

MSS agent will capture all messages from stdout and stderr to display them in
the web interface in real time when the script runs. When the script ends a
configuration summary with warnings and errors can be displayed to the user.

MSS checks every line in the script output to get a code corresponding to a message level. For
example ``echo "8Webmail RoundCube is activated on your server."`` is a info level
message that will be displayed in the configuration summary in bold.

Other codes :

* 1 : warning level code
* 2 : error level code
* 7 : info level code
* 8 : info level code (bold output)

Other messages won't be displayed in the configuration summary but in the detailed
output.

String replacement
^^^^^^^^^^^^^^^^^^

MSS will replace some tags and patterns to have a better output

+------------------------+----------------------------------------------------+
| TAG / Pattern          | Replacement                                        |
+========================+====================================================+
| @HOSTNAME@             | Replace with the server IP or name                 |
+------------------------+----------------------------------------------------+
| @BR@                   | Replace with html <br />                           |
+------------------------+----------------------------------------------------+
| @B@text@B@             | Replace with <strong>text</strong>                 |
+------------------------+----------------------------------------------------+
| http://foo.com         | Replace with an html link                          |
+------------------------+----------------------------------------------------+

