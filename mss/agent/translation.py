import gettext
import os
import locale

class TranslationManager:

    def __init__(self):
        #self.lang = ""
        # set default locale when starting agent
        self.lang = locale.getdefaultlocale()[0]
        self.catalogs = {}

    def set_lang(self, lang):
        self.lang = lang
        for name, infos in self.catalogs.items():
            (path, catalog) = infos
            self.set_catalog(name, path)

    def set_catalog(self, name, path=''):
        try:
            translation = gettext.translation(
                    name,
                    os.path.join(path, "locale"),
                    languages=[self.lang],
                    )
        except AttributeError:
            translation = gettext.NullTranslations()        
        except IOError:
            translation = gettext.NullTranslations()
        self.catalogs[name] = (path, translation)

    def translate(self, string, catalog):
        """Translate a given string to the language of the application."""
        try:
            if self.catalogs[catalog][1] is None:
                return unicode(string)
        except KeyError:
            return unicode(string)
        else:
            return self.catalogs[catalog][1].ugettext(string)    
