MSS architecture
=================================================

MSS is composed of two parts :

1. a XML-RPC agent which execute commands on the computers and manipulate the data. The agent is written in Python.
2. a webserver providing an interface to control the XML-RPC agent. The webserver is `cherrypy <http://www.cherrypy.org/>`_ and the interface is written with `Django <http://www.djangoproject.com>`_.

MSS XML-RPC agent (mss.agent python package)
-------------------------------------------------

The XML-RPC agent handles all the modules that can be installed through MSS. A module
is the description of a component you would like to install and configure in the MSS
interface.

A module is characterized by :

1. name
2. description
3. rpm packages
4. medias to add in order to install the packages
5. dependencies with other MSS modules
6. conflicts with other MSS modules
7. configuration fields for user input
8. a shell script to do the configuration

Most of this information is written in an JSON file. For example, this is the description of
the mysql module:

.. highlight:: javascript

::

    {
        "slug": "mysql",
        "name": "MySQL database",
        "description": "MySQL relational database",
        "packages": [
            {
                "name": "all",
                "rpms": ["mysql", "mysql-client"]
            }
        ],
        "conflict": ["mysqlmax"],
        "config": [
            {
                "type": "password",
                "name": "current_mypasswd",
                "show": "configured",
                "label": "Current password",
                "help": "Current MySQL root password."
            },
            {
                "type": "password",
                "name": "mypasswd",
                "require": "yes",
                "label": "New password",
                "help": "New MySQL root password. Set here the new password"
            }
        ],
        "standalone": false
    }

For mor detailled info check :doc:`module_description`

MSS web interface (mss.www python package)
-------------------------------------------------

The MSS web interface is served by the cherrypy webserver. Django is used on top of
cherrypy as it provides nice features for templating, url naming, internationalization,
authentication backends in a modular approach.
