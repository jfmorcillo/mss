Internationalization
====================

MSS uses gettext facilities for internationalization support.

Translation files must be located in ``locale/<lang>/LC_MESSAGES/<module_name>.po`` in
the module's directory.

You can use the ``build_pot.sh`` script to extract the strings of ``desc.xml`` to create
the modules po file thanks to ``xml2po``.

To translate the configuration script output, just add the strings in
the ``desc.xml`` file in ``<text>`` nodes :

.. highlight:: xml

::

    <module id="module">
        <name>My module</name>
        [ ... ]
        <text>started succesfully.</text>
        <text>fails starting. Check</text>
        <text>Mandriva Directory Server is running.</text>
        <text>You can log in the MDS interface from http://@HOSTNAME@/mmc/.</text>
        <text>MDS administrator : root</text>
    </module>
