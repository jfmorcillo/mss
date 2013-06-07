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

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.translation import ugettext as _, activate

from mss.lib.xmlrpc import XmlRpc

from lib.jsonui.response import JSONResponse
from transaction import Transaction, Steps, State

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
        xmlrpc.call('set_lang', lang)
    # redirect to url if supplied in GET
    if url:
        return HttpResponseRedirect(url)
    elif 'HTTP_REFERER' in request.META:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        return HttpResponseRedirect("/")

def mylogin(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('sections'))

    if request.method == "POST":
        user = authenticate(username=request.POST['username'],
                            password=request.POST['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                # redirect
                return HttpResponseRedirect(reverse('sections'))
        # invalid user
        xmlrpc.call('check_net')
        return render(request, 'login.html', {'error': True, 'first_time': True})
    else:
        first_time = xmlrpc.call('get_option', 'first-time')
        lang = xmlrpc.call('get_lang')
        set_lang(request, lang)
        # show login form
        xmlrpc.call('check_net')
        return render(request, 'login.html', {'first_time': first_time})

def mylogout(request):
    logout(request)
    xmlrpc.call('logout')
    return HttpResponseRedirect(reverse('login'))

def first_time_required(function):
    # Check if we need to run the first-time
    # installation
    def wrap(request, *args, **kwargs):
        first_time = xmlrpc.call('get_option', 'first-time')
        if not first_time:
            transaction = Transaction(request, ['mds_mmc'])
            if isinstance(transaction.steps, HttpResponseRedirect):
                return transaction.steps
            else:
                # Custom transaction for first-time
                transaction.update_step({
                    'id': Steps.PREINST,
                    'title': _('Welcome'),
                    'info': _('Before you can install any services we need to setup a few things with you.'),
                    'show_modules': False
                })
                return HttpResponseRedirect(reverse('preinst'))
        else:
            return function(request, *args, **kwargs)
    return wrap

# get agent status with Ajax long polling
def get_status(request):
    """ get agent status """
    global output
    TIMEOUT = 0
    # max request time
    MAX_TIME = 5
    while 1:
        sts = xmlrpc.call('get_status')
        if sts:
            # if status change or request reached MAX_TIME
            # or we force the update
            # send the status
            if sts != output["status"] or \
               request.GET['force'] == 'true' or \
               TIMEOUT >= MAX_TIME:
                output["status"] = sts
                return render(request, 'raw_output.html', {'output': sts})
            # wait for new status
            else:
                TIMEOUT += 1
                time.sleep(1)
        else:
            return HttpResponseBadRequest(_("MSS agent is unreacheable."))

def get_state(request, thread, module):
    """ used to get any thread result code and output """
    result = xmlrpc.call('get_state', thread, module)
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
    # get section list
    sections = xmlrpc.call('get_sections')
    # render the main page with all sections
    return render(request, 'sections.html', {'sections': sections})

@first_time_required
@login_required
def section(request, section):
    """ render section page """
    categories = xmlrpc.call('get_section', section)

    # format management url
    for category in categories:
        for module in category["modules"]:
            if "actions" in module:
                for action in module["actions"]:
                    if action['type'] == "link":
                        action['value'] = toHtml(request, action['value'], False)

    return render(request, 'section.html', {'section': section, 'categories': categories})

@login_required
def prepare(request):
    """ prepare the transaction """
    if request.method == "POST":
        modules = []
        for module, value in request.POST.items():
            modules.append(module)
        transaction = Transaction(request, modules)
        return HttpResponseRedirect(transaction.first_step_url())
    else:
        return HttpResponseRedirect(reverse('sections'))

@login_required
def preinst(request):
    """ preinst page """
    transaction = Transaction(request)
    transaction.set_current_step(Steps.PREINST)
    if transaction.current_step()['state'] in (State.DONE, State.DISABLED):
        return HttpResponseRedirect(transaction.next_step_url())

    return render(request, 'preinst.html', {'transaction': transaction})

@login_required
def download(request):
    transaction = Transaction(request)
    transaction.set_current_step(Steps.DOWNLOAD)
    if transaction.current_step()['state'] in (State.DONE, State.DISABLED):
        return HttpResponseRedirect(transaction.next_step_url())

    return render(request, 'download.html', {'transaction': transaction})

@login_required
def download_module(request, module):
    xmlrpc.call("download_module", module)
    return HttpResponse("")

@login_required
def medias_auth(request):
    """ media auth page """
    transaction = Transaction(request)
    transaction.set_current_step(Steps.MEDIAS_AUTH)
    if transaction.current_step()['state'] in (State.DONE, State.DISABLED):
        return HttpResponseRedirect(transaction.next_step_url())

    return render(request, 'media_auth.html', {'transaction': transaction})

@login_required
def medias_add(request):
    """ media add page """
    transaction = Transaction(request)
    transaction.set_current_step(Steps.MEDIAS_ADD)
    if transaction.current_step()['state'] in (State.DONE, State.DISABLED):
        return HttpResponseRedirect(transaction.next_step_url())

    if request.method == "POST":
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
    else:
        username = None
        password = None

    repositories = xmlrpc.call('get_repositories', transaction.modules_list)

    return render(request, 'media_add.html',
                  {'transaction': transaction, 'repositories': repositories,
                   'username': username, 'password': password})

@login_required
def add_media(request, module, repository):
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    xmlrpc.call("add_repository", module, repository, username, password)
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
    if transaction.current_step()['state'] in (State.DONE, State.DISABLED):
        return HttpResponseRedirect(transaction.next_step_url())

    # launch modules install
    xmlrpc.call('install_modules', transaction.modules_list)
    return render(request, 'install.html', {'transaction': transaction})

@login_required
def reload_packages(request):
    xmlrpc.call('load_packages')
    return HttpResponse("")

@login_required
def config(request):
    """ configuration page """
    transaction = Transaction(request)
    transaction.set_current_step(Steps.CONFIG)
    if transaction.current_step()['state'] in (State.DONE, State.DISABLED):
        return HttpResponseRedirect(transaction.next_step_url())

    config = xmlrpc.call('get_config', transaction.modules_list)

    run_config = False
    skip_config = True
    for module in transaction.modules_info:
        if module["has_configuration"]:
            skip_config = False
        if module["has_configuration_script"]:
            run_config = True

    # modules don't have configuration scripts
    if not run_config:
        for module in transaction.modules_list:
            config_end(request, module)
        return render(request, 'config_no.html', {'transaction': transaction})
    # some module have configuration
    elif not skip_config:
        return render(request, 'config.html', {'transaction': transaction, 'config': config})
    else:
        return HttpResponseRedirect(reverse('config_valid'))

@login_required
def config_valid(request):
    """ check user configuration """
    transaction = Transaction(request)
    transaction.set_current_step(Steps.CONFIG)
    if transaction.current_step()['state'] in (State.DONE, State.DISABLED):
        return HttpResponseRedirect(transaction.next_step_url())

    # get forms values
    config = {}
    for name, value in request.POST.items():
        config[name] = value
    # validate values
    errors = False
    config = xmlrpc.call('valid_config', transaction.modules_list, config)
    for conf in config:
        if conf["errors"]:
            errors = True
            break
    if errors:
        return render(request, 'config.html', {'config': config,
                                               'transaction': transaction})
    else:
        return render(request, 'config_run.html', {'config': config,
                                                   'transaction': transaction})

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
    # FIXME
    if module == "mds_mmc":
        xmlrpc.call('set_option', 'first-time', 'yes')
    return HttpResponse("")

@login_required
def reboot_run(request):
    xmlrpc.call('reboot')
    return HttpResponse("")

@login_required
def end(request):
    transaction = Transaction(request)
    transaction.set_current_step(Steps.END)

    for module in transaction.modules_list:
        xmlrpc.call('end_config', module, 0, "")

    return render(request, 'end.html',
                  {'transaction': transaction})

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
