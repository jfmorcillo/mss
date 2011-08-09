Module description
=================================================

The modules are located in the mss.agent.modules python package.

A module directory contains :

- a XML file describing the module, ``desc.xml``
- an ``__init__.py`` file
- some python functions to retrieve the current configuration in the ``__init__.py`` file (optional)
- locales
- a setup script (optional)
- templates files used by the setup script (optional)

The desc.xml file
-------------------------------------------------

For full examples of the ``desc.xml`` file check-out the :doc:`module_desc_example` page.

.. highlight:: xml

Basic description
^^^^^^^^^^^^^^^^^

The XML root is defined by a <module> node. The id parameter use the
same name as the module name

::

 <module id="module">
    <name>My module</name>
    <desc>A great module</desc>

Medias
^^^^^^

MSS allows you to add medias on the system to install packages.

* @verbose_name : name displayed in the web interface when adding the media
* @name : name used in the urmpi.cfg file
* @auth (optional) : None (default) | my
* @proto : http (default) | https
* @mode (optional) : None (default) | distrib | updates

@ARCH@ will be replaced by the machine arch (x86_64 or i586).

::

    <medias verbose_name="My module" name="module" auth="my" proto="https">
        <url>download.mandriva.com/EnterpriseServer5/rpms/@ARCH@/</url>
    </medias>


Packages
^^^^^^^^

Your module may install some packages. The packages can be arch dependant.

* @name : i586 | x86_64 | all

::

    <packages>
        <target name="all">
            <rpm>openldap-servers</rpm>
            <rpm>openldap-clients</rpm>
        </target>
        <target name="i686">
            <rpm>libsasl2-plug-gssapi</rpm>
        </target>
        <target name="x86_64">
            <rpm>lib64sasl2-plug-gssapi</rpm>
        </target>
    <packages>


Conflicts
^^^^^^^^^

If the module conflicts with other modules in MSS.

::

    <conflicts>
        <module>some_module</module>
    </conflicts>


Dependencies
^^^^^^^^^^^^

You can add dependencies with other modules. If some module is added as a
dependency it will be installed and configured before the current module.

::

    <deps>
        <modules>some_other_module</modules>
    </deps>


Module configuration
^^^^^^^^^^^^^^^^^^^^

The module configuration may need some information provided by the user. Several
field can be used to gather the information needed to run a configuration script.

Configuration definition starts with :

::

    <config>

Then add some form fields.

Simple text field
"""""""""""""""""

* @name : field name
* @require : the field is mandatory (optional)
* @default : default value for the field - can be a string or a custom method (optional)
* @validation : fqdn | ip | custom method (validate the field data - optional)
* @show_if_unconfigured : the field won't be displayed on reconfiguration (optional)
* @edit_if_unconfigured : the field won't be editable on reconfiguration (optional)

::

    <text name="param1" require="yes" default="default_text" validation="ip">
        <label>Param 1</label>
        <help>Some help on param 1</help>
    </text>

The custom method for validation or default value must be declared in the
module's __init__.py file.

Password field
""""""""""""""

The generated form will add automatically a second password field to validate
the password

* @name : field name
* @require : the field is mandatory (optional)
* @default : default value for the field - can be a string or a custom method (optional)
* @show_if_unconfigured : the field won't be displayed on reconfiguration (optional)

::

    <password name="password" require="yes" default="default_pass">
        <label>Password</label>
        <help>Some help on password</help>
    </password>

Multi text field
""""""""""""""""

* @name : field name
* @multi : yes | no (add/remove fields buttons)
* @require : yes | no (the field is mandatory - optional)
* @default : default value for the field - can be a string or a custom method (optional)
* @validation : fqdn | ip | custom method (validate the field data - optional)
* @show_if_unconfigured : the field won't be displayed on reconfiguration (optional)

::

    <text name="param2" multi="yes" default="text1;text2;text3">
        <label>Param 2</label>
        <help>Some help on param 2</help>
    </text>

Network field
"""""""""""""

This special field let the user input a network description (ip/netmask)

* @name : field name
* @format : long | short (/24 or /255.255.255.0 - format used in the config script)
* @default : default value for the field - can be a string or a custom method (optional)
* @validation : network (optional)
* @show_if_unconfigured : the field won't be displayed on reconfiguration (optional)

::

    <network name="param3" format="short" validation="network">
        <label>Param 3</label>
        <help>Some help on param 3</help>
    </network>

Select list field
"""""""""""""""""

* @name : field name
* @require : yes | no (mandatory field - optional)
* @default : default selected value - can be a string or a custom method (optional)
* @show_if_unconfigured : the field won't be displayed on reconfiguration (optional)

::

    <options name="param4" require="yes">
        <label>Param 4</label>
        <help>Some help on param 4</help>
        <option value="option1">Option 1</option>
        <option value="option2">Option 2</option>
        <option value="option3">Option 3</option>
    </options>

Checkbox field
""""""""""""""

* @name : field name
* @default : on | off
* @show_if_unconfigured : the field won't be displayed on reconfiguration (optional)

::

    <check name="param5" default="on">
        <label>Param 5</label>
        <help>Some help on param 5</help>
    </check>


For full examples of the ``desc.xml`` file check-out the :doc:`module_desc_example` page.

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
configuration description in ``desc.xml``.

If you want to retrieve the current configuration of the module when re-configuring
the module in MSS you have to write a :py:func:`get_current_config` function.

.. py:function:: get_current_config()

    Returns current configuration of the module

    :rtype: dict { "param1": value, "param2": value, ... }


The values returned by this function replaces the default values set in in the
configuration description in ``desc.xml``. Have a look in ``mds_*`` modules for some examples.

Example of ``mds_mmc`` module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Configuration definition in ``desc.xml`` :

::

    <config>
        <text name="mdsdomain" require="yes" default="example.com" validation="fqdn">
            <label>MDS domain name</label>
            <help>Usually the domain name (eg: domain.com) managed with MDS.
            This define the LDAP root.</help>
        </text>
        <password name="mdspasswd" require="yes">
            <label>MDS password</label>
            <help>The MDS admin password.</help>
        </password>
        <check name="mdsppolicy" default="on">
            <label>Password policy</label>
            <help>Enable password policy on MDS (password age, expiration,
            history, lock-out...)</help>
        </check>
    </config>


``__init__.py`` file :

.. literalinclude:: ../../mss/agent/modules/mds_mmc/__init__.py
    :language: py

The setup script and templates
-------------------------------------------------

To run modules configuration the MSS agent runs shell scripts as root in the
background. The script name and its parameters launch by MSS have to be declared in the :py:func:`get_config_info` function.

``mds_webmail`` script example :

.. literalinclude:: ../../mss/agent/modules/mds_webmail/setup-webmail.sh
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

