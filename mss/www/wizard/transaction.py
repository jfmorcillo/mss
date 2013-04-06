import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _, ungettext

from mss.www.xmlrpc import XmlRpc

xmlrpc = XmlRpc()
logger = logging.getLogger(__name__)


class Steps:
    PREINST = "preinst"
    DOWNLOAD = "download"
    MEDIAS_AUTH = "medias_auth"
    MEDIAS_ADD = "medias_add"
    INSTALL = "install"
    CONFIG = "config"
    REBOOT = "reboot"
    END = "end"


class Transaction(object):

    def __init__(self, request, modules_list=[]):
        if modules_list:
            self.modules_list = modules_list
        else:
            self.modules_list = request.session['modules_list']
        self.setup()
        self.save(request)

    def setup(self):
        err, result = xmlrpc.call('preinstall_modules', self.modules_list)
        if not err:
            self.modules_info = result
            self.modules_list = [m['slug'] for m in self.modules_info]
        else:
            self.transaction = err
            return

        self.transaction = [
            {
                'id': Steps.PREINST,
                'disabled': False,
                'title': _("Installation summary"),
                'info': ungettext(
                            "The folowing addon will be installed.",
                            "The folowing addons will be installed.",
                            len(self.modules_list)
                        ),
                'show_modules': True,
                'current': False
            },
            {
                'id': Steps.DOWNLOAD,
                'disabled': True,
                'title': _("Addon download"),
                'info': _("Download addons from the ServicePlace"),
                'current': False,
            },
            {
                'id': Steps.MEDIAS_AUTH,
                'disabled': True,
                'title': _("Medias authentication"),
                'info': _("One or more medias need authentication"),
                'current': False,
            },
            {
                'id': Steps.MEDIAS_ADD,
                'disabled': True,
                'title': _("Medias add"),
                'info': "",
                'current': False,
            },
            {
                'id': Steps.INSTALL,
                'disabled': True,
                'title': _("Installation"),
                'info': "",
                'current': False,
            },
            {
                'id': Steps.CONFIG,
                'disabled': True,
                'title': _("Initial configuration"),
                'info': "",
                'current': False
            },
            {
                'id': Steps.REBOOT,
                'disabled': True,
                'title': _("Reboot"),
                'current': False
            },
            {
                'id': Steps.END,
                'disabled': True,
                'title': _("End of installation"),
                'current': False
            }
        ]

        for module in self.modules_info:
            if not module['installed'] or not module["downloaded"]:
                self.enable_step(Steps.INSTALL)
                logger.debug("Module %s is not installed or not downloaded: enabling install step" % module["slug"])
            if not module["downloaded"]:
                self.enable_step(Steps.DOWNLOAD)
                logger.debug("Module %s is not downloaded: enabling download step" % module["slug"])
            if module['reboot']:
                logger.debug("Module %s need to reboot the system: enabling reboot step" % module["slug"])
                self.enable_step(Steps.REBOOT)
            else:
                self.enable_step(Steps.END)

        err, result = xmlrpc.call('get_repositories', self.modules_list)
        if not err:
            self.repositories = result
            for repository in self.repositories:
                if repository['restricted']:
                    self.enable_step(Steps.MEDIAS_AUTH)
                    break
            if self.repositories:
                self.enable_step(Steps.MEDIAS_ADD)

        if self.find_step(Steps.DOWNLOAD)['disabled']:
            for module in self.modules_info:
                if module["has_configuration"] or module["has_configuration_script"]:
                    logger.debug("Module %s needs configuration: enabling config step" % module['slug'])
                    self.enable_step(Steps.CONFIG)
                    break
        else:
            logger.debug("Some module is not downloaded: enabling config step")
            self.enable_step(Steps.CONFIG)

    def save(self, request):
        request.session['modules_list'] = self.modules_list

    def find_step(self, step):
        for s in self.transaction:
            if s['id'] == step:
                return s
        raise Exception("Step does not exist ?!")

    def disable_step(self, step):
        self.find_step(step)['disabled'] = True

    def enable_step(self, step):
        self.find_step(step)['disabled'] = False

    def update_step(self, step):
        for s in self.transaction:
            if s['id'] == step['id']:
                for key, value in step.items():
                    s[key] = value

    def current_step(self):
        for s in self.transaction:
            if s['current']:
                return s

    def set_current_step(self, step):
        for s in self.transaction:
            if s['id'] == step:
                s['current'] = True
            else:
                s['current'] = False

    def first_step(self):
        for step in self.transaction:
            if not step['disabled']:
                return step

    def next_step(self):
        next = False
        for step in self.transaction:
            if next and not step['disabled']:
                return step
            if step['current']:
                next = True
        # no next step, return home
        return {'id': 'sections'}

    def next_step_url(self):
        return reverse(self.next_step()['id'])

    def first_step_url(self):
        return reverse(self.first_step()['id'])

    def current_step_url(self):
        return reverse(self.current_step()['id'])
