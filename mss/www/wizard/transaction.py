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


class State:
    DISABLED = -1
    TODO = 0
    DONE = 1


class Transaction(object):

    def __init__(self, request, modules_list=[]):
        if modules_list:
            self.modules_list = modules_list
            self.setup()
        else:
            self.modules_list = request.session['modules_list']
            self.steps = request.session['steps']
            self.update()
        self.save(request)

    def setup(self):
        err, result = xmlrpc.call('preinstall_modules', self.modules_list)
        if not err:
            self.modules_info = result
            self.modules_list = [m['slug'] for m in self.modules_info]
        else:
            self.steps = err
            return

        self.steps = [
            {
                'id': Steps.PREINST,
                'state': State.TODO,
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
                'state': State.DISABLED,
                'title': _("Addon download"),
                'info': _("Download addons from the ServicePlace"),
                'current': False,
            },
            {
                'id': Steps.MEDIAS_AUTH,
                'state': State.DISABLED,
                'title': _("Medias authentication"),
                'info': _("One or more medias need authentication"),
                'current': False,
            },
            {
                'id': Steps.MEDIAS_ADD,
                'state': State.DISABLED,
                'title': _("Medias add"),
                'info': "",
                'current': False,
            },
            {
                'id': Steps.INSTALL,
                'state': State.DISABLED,
                'title': _("Installation"),
                'info': "",
                'current': False,
            },
            {
                'id': Steps.CONFIG,
                'state': State.DISABLED,
                'title': _("Initial configuration"),
                'info': "",
                'current': False
            },
            {
                'id': Steps.REBOOT,
                'state': State.DISABLED,
                'title': _("Reboot"),
                'current': False
            },
            {
                'id': Steps.END,
                'state': State.DISABLED,
                'title': _("End of installation"),
                'current': False
            }
        ]

        for module in self.modules_info:
            if not module['installed'] or not module["downloaded"]:
                self.todo_step(Steps.INSTALL)
                logger.debug("Module %s is not installed or not downloaded: todo install step" % module["slug"])
            if not module["downloaded"]:
                self.todo_step(Steps.DOWNLOAD)
                logger.debug("Module %s is not downloaded: todo download step" % module["slug"])
            if module['reboot']:
                logger.debug("Module %s need to reboot the system: enabling reboot step" % module["slug"])
                self.todo_step(Steps.REBOOT)
            else:
                self.todo_step(Steps.END)

        err, result = xmlrpc.call('get_repositories', self.modules_list)
        if not err:
            self.repositories = result
            for repository in self.repositories:
                if repository['restricted']:
                    self.todo_step(Steps.MEDIAS_AUTH)
                    break
            if self.repositories:
                self.todo_step(Steps.MEDIAS_ADD)

        if self.find_step(Steps.DOWNLOAD)['state'] == State.TODO:
            logger.debug("Some module is not downloaded: todo config step")
            self.todo_step(Steps.CONFIG)
        else:
            for module in self.modules_info:
                if module["has_configuration"] or module["has_configuration_script"]:
                    logger.debug("Module %s needs configuration: todo config step" % module['slug'])
                    self.todo_step(Steps.CONFIG)
                    break

    def update(self):
        err, result = xmlrpc.call('get_modules_details', self.modules_list)
        if not err:
            self.modules_info = result

        err, result = xmlrpc.call('get_repositories', self.modules_list)
        if not err:
            self.repositories = result

        downloaded = True
        medias_auth = True
        medias_added = True
        installed = True
        configured = True

        for module in self.modules_info:
            if not module['downloaded']:
                downloaded = False
                break
        if self.get_state_step(Steps.DOWNLOAD) == State.TODO and downloaded:
            self.done_step(Steps.DOWNLOAD)

        for module in self.modules_info:
            if not module['installed']:
                installed = False
                break
        if self.get_state_step(Steps.INSTALL) == State.TODO and installed:
            self.done_step(Steps.INSTALL)

        if self.repositories:
            medias_added = False
            for repository in self.repositories:
                if repository['restricted']:
                    medias_auth = False
                    break
        if self.get_state_step(Steps.MEDIAS_AUTH) == State.TODO and medias_auth:
            self.done_step(Steps.MEDIAS_AUTH)
        if self.get_state_step(Steps.MEDIAS_ADD) == State.TODO and medias_added:
            self.done_step(Steps.MEDIAS_ADD)

        for module in self.modules_info:
            if not module['configured']:
                configured = False
                break
        if self.get_state_step(Steps.CONFIG) == State.TODO and configured:
            self.done_step(Steps.CONFIG)

    def save(self, request):
        request.session['modules_list'] = self.modules_list
        request.session['steps'] = self.steps

    def find_step(self, step):
        for s in self.steps:
            if s['id'] == step:
                return s
        raise Exception("Step does not exist ?!")

    def get_state_step(self, step):
        return self.find_step(step)['state']

    def todo_step(self, step):
        self.find_step(step)['state'] = State.TODO

    def done_step(self, step):
        self.find_step(step)['state'] = State.DONE

    def update_step(self, step):
        for s in self.steps:
            if s['id'] == step['id']:
                for key, value in step.items():
                    s[key] = value

    def current_step(self):
        for s in self.steps:
            if s['current']:
                return s

    def set_current_step(self, step):
        for s in self.steps:
            if s['id'] == step:
                s['current'] = True
            else:
                s['current'] = False

    def first_step(self):
        for step in self.steps:
            if not step['state'] in (State.DONE, State.DISABLED):
                return step

    def next_step(self):
        next = False
        for step in self.steps:
            if next and not step['state'] in (State.DONE, State.DISABLED):
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
