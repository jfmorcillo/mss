Internationalization
====================

MSS uses gettext facilities for internationalization support.

Translation files must be located in ``locale/<lang>/LC_MESSAGES/<module_name>.po`` in
the module's directory.

You can use the ``build_pot.sh`` script to extract the strings of ``desc.json`` to create
the modules po file thanks to ``json2po``.

The strings marked for translation in the setup script are also extracted by this script.
We use the standard bash method to translate strings with gettext. In your setup script:

::

    info $"Administrator name : root"
    info $"Administrator password : $mypass"

You can also translate strings in the module python files like this:

::

    from mss.agent.managers.translation import TranslationManager
    _ = TranslationManager().translate

    _('Text to translate', 'module_slug')
