# -*- coding: UTF-8 -*-
#
# (c) 2010-2012 Mandriva, http://www.mandriva.com/
#
# This file is part of Mandriva Server Setup
#
# MSS is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MSS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MSS; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import re
import time
from sets import Set

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponse
from django.views.generic.simple import direct_to_template
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.translation import ugettext as _, activate

from mss.www.xmlrpc import XmlRpc

from lib.jsonui.response import JSONResponse
from transaction import Transaction, Steps

xmlrpc = XmlRpc()
output = {"status": ""}

# used to change interface + agent lang
def set_lang(request, lang):
    if "url" in request.GET:
        url = request.GET["url"]
    else:
        url = False
    if hasattr(request, 'session'):
        # set interface lang
        request.session['django_language'] = lang
        settings.DEFAULT_LANGUAGE = lang
        activate(lang)
        # set agent language
        err, result = xmlrpc.call('set_lang', lang)
    # redirect to url if supplied in GET
    if url:
        return HttpResponseRedirect(url)
    elif 'HTTP_REFERER' in request.META:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        return HttpResponseRedirect("/")

def mylogin(request):
    if request.method == "POST":
        username=username=request.POST['username']
        password=request.POST['password']
        user = authenticate(username=request.POST['username'],
                            password=request.POST['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                err, status = xmlrpc.call('get_authentication_token', username, password)
                if err:
                    return direct_to_template(request, 'invalid_login.html')
                err, status = xmlrpc.call('load')
                if err:
                    return direct_to_template(request, 'invalid_login.html')

                # redirect
                return HttpResponseRedirect(reverse('sections'))
        else:
            # disabled account
            xmlrpc.call('check_net')
            return direct_to_template(request, 'inactive_account.html')
    else:
        # invalid login
        xmlrpc.call('check_net')
        return direct_to_template(request, 'invalid_login.html')

def mylogout(request):
    logout(request)
    # reset language
    set_lang(request, settings.DEFAULT_LANGUAGE)
    return HttpResponseRedirect(reverse('first_time'))

def first_time(request):
    set_lang(request, settings.DEFAULT_LANGUAGE)
    # Check if first-time installation was done
    err, result = xmlrpc.call('get_option', 'first-time')
    if not result:
        request.session['first-time'] = False;
    else:
        request.session['first-time'] = True;

    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('sections'))

    if not request.session['first-time']:
        xmlrpc.call('check_net')
        return direct_to_template(request, 'first_time.html')
    else:
        return HttpResponseRedirect(reverse('login_form'))

def login_form(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('sections'))
    else:
        xmlrpc.call('check_net')
        return render_to_response('login.html',
            context_instance=RequestContext(request))

def first_time_required(function):
    # Check if we need to run the first-time
    # installation
    def wrap(request, *args, **kwargs):
        # flush some user session data
        for key in ('modules', 'modules_info', 'transaction'):
            try:
                del request.session[key]
            except KeyError:
                pass
        if not 'first-time' in request.session or not request.session['first-time']:
            transaction = Transaction(request, ['mds_mmc'])
            if isinstance(transaction.transaction, HttpResponseRedirect):
                return transaction.transaction
            else:
                # Custom transaction for first-time
                transaction.update_step({
                    'id': Steps.PREINST,
                    'title': _('Welcome'),
                    'info': _('Before you can install any services we need to setup a few things with you.'),
                    'show_modules': False
                })
                return HttpResponseRedirect(reverse('prepare'))
        else:
            return function(request, *args, **kwargs)

    return wrap

def error(request, code):
    """ error page """
    return render_to_response('error.html', {'code': code},
        context_instance=RequestContext(request))

# get agent status with Ajax long polling
def get_status(request):
    """ get agent status """
    global output
    TIMEOUT = 0
    # max request time
    MAX_TIME = 5
    while 1:
        err, sts = xmlrpc.call('get_status')
        if sts:
            # if status change or request reached MAX_TIME
            # or we force the update
            # send the status
            if sts != output["status"] or \
               request.GET['force'] == 'true' or \
               TIMEOUT >= MAX_TIME:
                output["status"] = sts
                return render_to_response('raw_output.html',
                    {'output': sts},
                    context_instance=RequestContext(request))
            # wait for new status
            else:
                TIMEOUT += 1
                time.sleep(1)
        else:
            return HttpResponseBadRequest(_("MSS agent is unreacheable."))

def get_state(request, thread, module):
    """ used to get any thread result code and output """
    err, result = xmlrpc.call('get_state', thread, module)
    if err:
        return err
    else:
        code = result[0]
        output = result[1]
        for line in output:
            if "text" in line:
                line["text"] = toHtml(request, line["text"])
    return JSONResponse({'code': code, 'output': output})

def has_net(request, has_net):
    """ Run some actions if we have the connection or not """
    request.session['has_net'] = False
    if int(has_net) == 0:
        # update the medias if net is ok
        xmlrpc.call("update_medias")
        request.session['has_net'] = True

    return HttpResponse("")

@first_time_required
@login_required
def sections(request):
    """ sections list """
    sections = []
    # get section list
    err, result = xmlrpc.call('get_sections')
    if err:
        return err
    sections = result

    # render the main page with all sections
    return render_to_response('sections.html',
        {'sections': sections},
        context_instance=RequestContext(request))

@first_time_required
@login_required
def section(request, section):
    """ render section page """
    err, result = xmlrpc.call('get_section', section)
    if err:
        return err
    section_info = result

    section_modules = []
    for bundle in section_info['bundles']:
        for module in bundle["modules"]:
             section_modules.append(module)

    err, result = xmlrpc.call('get_modules', section_modules)
    if err:
        return err
    else:
        # detailed modules list
        modules = result
        # check module access
        # format management url
        for module in modules:
            # Check if modules is already installer
            for action in module['actions']:
                if action['type'] == "link":
                    action['value'] = toHtml(request, action['value'], False)

        err, result = xmlrpc.call('get_sections')
        if err:
            return err
        sections = result

        # Translate section name
        for section in sections:
            section["name"] = _(section["name"])

        return render_to_response('section.html',
            {'sections': sections, 'section': section_info,
            'modules': modules },
            context_instance=RequestContext(request))

@login_required
def prepare(request):
    """ prepare the transaction """
    if request.method == "POST":
        modules = []
        for module, value in request.POST.items():
            modules.append(module)
    else:
        try:
            modules = request.session['modules_list']
        except KeyError:
            return HttpResponseRedirect(reverse('sections'))

    transaction = Transaction(request, modules)
    return HttpResponseRedirect(transaction.first_step_url())

@login_required
def preinst(request):
    """ preinst page """
    transaction = Transaction(request)
    transaction.set_current_step(Steps.PREINST)
    if transaction.current_step()['disabled']:
        return HttpResponseRedirect(transaction.next_step_url())

    return render_to_response('preinst.html', {'transaction': transaction},
                              context_instance=RequestContext(request))

@login_required
def medias(request):
    """ media auth page """
    transaction = Transaction(request)
    transaction.set_current_step(Steps.MEDIAS)
    if transaction.current_step()['disabled']:
        return HttpResponseRedirect(transaction.next_step_url())

    err, result = xmlrpc.call('get_medias', transaction.modules)
    if err:
        return err
    else:
        medias = result
        if medias:
            # check if we need authentication
            auths = Set()
            can_skip = False
            for media in medias:
                if 'auth' in media and media['auth']:
                    auths.add(media['auth'])
                if 'can_skip' in media and media['can_skip']:
                    can_skip = True
            if auths:
                return render_to_response('media_auth.html',
                        {'can_skip': can_skip, 'auths': auths,
                         'transaction': transaction},
                        context_instance=RequestContext(request))
            else:
                return render_to_response('media_add.html',
                        {'medias': medias, 'transaction': transaction},
                        context_instance=RequestContext(request))
        else:
            return HttpResponseRedirect(transaction.next_step_url())

@login_required
def medias_add(request):
    """ media add page """
    transaction = Transaction(request)
    transaction.set_current_step(Steps.MEDIAS_ADD)
    if transaction.current_step()['disabled']:
        return HttpResponseRedirect(transaction.next_step_url())

    err, result = xmlrpc.call('get_medias', transaction.modules)
    if err:
        return err
    else:
        medias = result
        if request.method == "POST":
            for media in medias:
                if media["auth"]:
                    media['username'] = request.POST[media['auth']+'_username']
                    media['password'] = request.POST[media['auth']+'_password']

        return render_to_response('media_add.html',
                {'medias': medias, 'transaction': transaction},
                context_instance=RequestContext(request))

@login_required
def add_media(request, module):
    if request.method == "POST":
        if 'username' in request.POST:
            username = request.POST["username"]
            password = request.POST["password"]
        else:
            username = None
            password = None
        xmlrpc.call("add_media", module, username, password)
    return HttpResponse("")

@login_required
def medias_update(request):
    xmlrpc.call('update_medias')
    return HttpResponse("")

@login_required
def install(request):
    """ install page """
    transaction = Transaction(request)
    transaction.set_current_step(Steps.INSTALL)

    if transaction.current_step()['disabled']:
        return HttpResponseRedirect(transaction.next_step_url())

    # launch modules install
    err, result = xmlrpc.call('install_modules', transaction.modules)
    if err:
        return err
    else:
        if result:
            return render_to_response('install.html',
                    {'transaction': transaction},
                    context_instance=RequestContext(request))

@login_required
def reload_packages(request):
    xmlrpc.call('load_packages')
    return HttpResponse("")

@login_required
def config(request):
    """ configuration page """
    transaction = Transaction(request)
    transaction.set_current_step(Steps.CONFIG)

    if transaction.current_step()['disabled']:
        return HttpResponseRedirect(transaction.next_step_url())

    err, result = xmlrpc.call('get_config', transaction.modules)
    if err:
        return err
    else:
        config = result

    # check if the modules needs configuration
    do_config = False
    # check if the modules have configuration scripts
    skip_config = True
    for m1 in config:
        for m2 in transaction.modules_info:
            if m1[0]['slug'] == m2['slug']:
                if m1[0].get('do_config'):
                    do_config = True
                if not m1[0].get('skip_config'):
                    skip_config = False
                # store in the module list skip_config
                # information for config_run view
                m2['skip_config'] = m1[0].get('skip_config')
    transaction.save(request)
    # all modules does'nt have a configuration script
    if skip_config:
        for module in transaction.modules:
            config_end(request, module)
        return render_to_response('config_no.html',
            {'transaction': transaction},
            context_instance=RequestContext(request));
    # some module have a configuration
    elif do_config:
        return render_to_response('config.html',
            {'config': config, 'transaction': transaction},
            context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('config_valid'))

@login_required
def config_valid(request):
    """ check user configuration """
    transaction = Transaction(request)

    do_config = False
    # redirect if configuration is already done
    for module in transaction.modules_info:
        if not module['configured']:
            do_config = True

    if not do_config:
        return HttpResponseRedirect(transaction.next_step_url())

    # get forms values
    config = {}
    for name, value in request.POST.items():
        config[name] = value
    # validate values
    err, result = xmlrpc.call('valid_config', transaction.modules, config)
    if err:
        return err
    else:
        errors = result[0]
        config = result[1]
    if errors:
        return render_to_response('config.html',
                {'config': config, 'transaction': transaction},
                context_instance=RequestContext(request))
    else:
        return render_to_response('config_run.html',
                {'config': config, 'transaction': transaction},
                context_instance=RequestContext(request))

@login_required
def config_run(request, module):
    """ run configuration script for module """
    transaction = Transaction(request)
    for m in transaction.modules_info:
        if m['slug'] == module and not m['configured']:
            xmlrpc.call('run_config', module)
            break
    return HttpResponse("")

@login_required
def config_end(request, module):
    """ tells the agent the module has been configured """
    xmlrpc.call('end_config', module)
    # FIXME
    if module == "mds_mmc":
        xmlrpc.call('set_option', 'first-time', 'yes')
        request.session['first-time'] = True;
    return HttpResponse("")

@login_required
def reboot(request):
    transaction = Transaction(request)
    transaction.set_current_step(Steps.REBOOT)

    if transaction.current_step()['disabled']:
        return HttpResponseRedirect(transaction.next_step_url())

    return render_to_response('reboot.html',
            {'transaction': transaction},
            context_instance=RequestContext(request))

@login_required
def reboot_run(request):
    xmlrpc.call('reboot')
    return HttpResponse("")

def toHtml(request, text, links = True):
    # replace hostname tag with server name
    text = re.sub('@HOSTNAME@', request.META['HTTP_HOST'].replace(':8000', ''), text);
    # new line replacement
    text = re.sub('@BR@', '<br/>', text);
    # bold support
    text = re.sub(r'@B@(.*)@B@', r'<strong>\1</strong>', text);
    if links:
        # make links
        text = re.sub(r'(https?:\/\/[^ <)]*)', r'<a href="\1">\1</a>', text);
    return text
