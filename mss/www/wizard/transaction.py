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

class Transaction:

    def __init__(self, request, modules = []):

        if 'transaction' in request.session:
            self.transaction = request.session['transaction']
            self.modules = request.session['modules_list']
            self.modules_info = request.session['modules_info']
            self.repositories = request.session['repositories']
            self.update_module_info()
        else:
            err, result = xmlrpc.call('preinstall_modules', modules)
            if err:
                self.transaction = err
            else:
                self.modules_info = result
                # update with depedencies
                self.modules = [ m['slug'] for m in self.modules_info ]
                self.reset()
                self.prepare()
                self.save(request)

    def reset(self):
        self.repositories = []
        self.transaction = [
            {
                'id': Steps.PREINST,
                'disabled': False,
                'title': _("Installation summary"),
                'info': ungettext(
                            "The folowing component will be installed.",
                            "The folowing components will be installed.",
                            len(self.modules)
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

    def prepare(self):
        err, result = xmlrpc.call('get_repositories', self.modules)
        if not err:
            self.repositories = result
            for repository in self.repositories:
                if repository['restricted']:
                    self.enable_step(Steps.MEDIAS_AUTH)
                    break
            if self.repositories:
                self.enable_step(Steps.MEDIAS_ADD)

        err, result = xmlrpc.call('get_modules_details', self.modules)
        if not err:
            self.modules_info = result
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

        if self.find_step(Steps.DOWNLOAD)['disabled']:
            err, result = xmlrpc.call('get_config', self.modules)
            for module in result:
                infos = module[0]
                if not infos['skip_config']:
                    logger.debug("Module %s needs configuration: enabling config step" % infos['slug'])
                    self.enable_step(Steps.CONFIG)
                    break
        else:
            logger.debug("Some module is not downloaded: enabling config step")
            self.enable_step(Steps.CONFIG)

    def save(self, request):
        request.session['transaction'] = self.transaction
        request.session['modules_list'] = self.modules
        request.session['modules_info'] = self.modules_info
        request.session['repositories'] = self.repositories

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

    def update_module_info(self):
        err, result = xmlrpc.call('preinstall_modules', self.modules)
        self.modules_info = result

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
