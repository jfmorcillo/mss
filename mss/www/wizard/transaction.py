from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _, ungettext
from xmlrpc import XmlRpc

xmlrpc = XmlRpc()

class Steps:
    PREINST = "preinst"
    MEDIAS = "medias"
    MEDIAS_ADD = "medias_add"
    INSTALL = "install"
    CONFIG = "config"

class Transaction:

    def __init__(self, request, modules = []):

        if 'transaction' in request.session:
            self.transaction = request.session['transaction']
            self.modules = request.session['modules_list']
            self.modules_info = request.session['modules_info']
        else:
            err, result = xmlrpc.call('preinstall_modules', modules)
            self.modules_info = result
            # update with depedencies
            self.modules = [ m['id'] for m in self.modules_info ]
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
                    'id': Steps.MEDIAS,
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
                    'title': _("Configuration"),
                    'info': "",
                    'current': False
                }
            ]
            self.prepare()
            self.save(request)

    def save(self, request):
        request.session['transaction'] = self.transaction
        request.session['modules_list'] = self.modules
        request.session['modules_info'] = self.modules_info

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
    
    def prepare(self):
        err, result = xmlrpc.call('get_medias', self.modules)
        for media in result:
            if 'auth' in media and media['auth']:
                self.enable_step(Steps.MEDIAS);
        if len(result) > 0:
            self.enable_step(Steps.MEDIAS_ADD);

        err, result = xmlrpc.call('get_modules', self.modules)
        for module in result:
            if not module['installed']:
                self.enable_step(Steps.INSTALL);
        
        err, result = xmlrpc.call('get_config', self.modules)
        print result
        for module in result:
            infos = module[0]
            if not infos['skip_config']:
                self.enable_step(Steps.CONFIG);

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
