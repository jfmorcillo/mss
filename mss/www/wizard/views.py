# -*- coding: UTF-8 -*-
#
# (c) 2010 Mandriva, http://www.mandriva.com/
#
# $Id$
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

import xmlrpclib
from datetime import datetime
import re
import time
from xml.sax import SAXParseException
from sets import Set

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponse, Http404
from django.views.generic.simple import direct_to_template
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.utils.translation import ugettext as _, activate

from lib.jsonui.response import JSONResponse
from config import ConfigManager
from xmlrpc import XmlRpc
#import rdflib

xmlrpc = XmlRpc()
CM = ConfigManager()
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

def mylogin(request):
    if request.method == "POST":
        lang = request.POST.get('language', None)
        user = authenticate(username=request.POST['username'],
            password=request.POST['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                # redirect
                return HttpResponseRedirect(reverse('sections'))
        else:
            # disabled account
            return direct_to_template(request, 'inactive_account.html')
    else:
        # invalid login
        return direct_to_template(request, 'invalid_login.html')

def mylogout(request):
    logout(request)
    # reset language
    set_lang(request, settings.DEFAULT_LANGUAGE)
    return HttpResponseRedirect(reverse('first_time'))

def first_time(request):
    set_lang(request, settings.DEFAULT_LANGUAGE)
    # first time check
    if len(User.objects.all()) == 0:
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
            return HttpResponseBadRequest(_("The XML-RPC server is not responding"))

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

@login_required
def sections(request):
    """ sections list """
    # render the main page with all sections
    return render_to_response('sections.html',
        {'sections': CM.get_sections(),
         'language_form': True },
        context_instance=RequestContext(request))

@login_required
def section(request, section):
    """ render section page """
    # flush some user session data
    for key in ('modules', 'modules_list'):
        try:
            del request.session[key]
        except KeyError:
            pass
    # get section
    section_info = CM.get_section(section)
    # get modules info for modules list
    err, result = xmlrpc.call('get_modules', CM.get_section_modules(section))
    if err:
        return err
    else:
        # detailed modules list
        modules = result
        # check module access
        for module in modules:
            module['access'] = True
            if module['infos']['buy'] and \
            not request.user.profile.has_family('mes5-get-%s' % module['id']):
                module['access'] = False
        # create simple modules list
        modules_list = [m.get('id') for m in modules]
        # remove modules not present server side
        for bundle in section_info["bundles"]:
            for module in bundle["modules"]:
                if module not in modules_list:
                    section['modules'].remove(module)

        return render_to_response('section.html',
            {'section': section_info,
            'modules': modules, 'language_form': True },
            context_instance=RequestContext(request))

@login_required
def preinst(request):
    """ preinst page """
    if request.method == "POST":
        # get module list
        modules = []
        for module, value in request.POST.items():
            modules.append(module)
        # get preinstall info for modules
        err, result = xmlrpc.call('preinstall_modules', modules)
        if err:
            return err
        else:
            modules = result
            # store module info in session
            request.session['modules'] = modules
            request.session['modules_list'] = [m.get('id') for m in modules]
            return render_to_response('preinst.html',
                {'modules': modules},
                context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('sections'))

@login_required
def medias(request, module=None):
    """ media page """
    # direct call with module
    # mainly for MES5 media add
    if module:
        request.session['modules_list'] = [module]
        # get preinstall info for modules
        err, result = xmlrpc.call('preinstall_modules', [module])
        if err:
            return err
        else:
            modules = result
        request.session['modules'] = modules

    modules_list = request.session['modules_list']
    err, result = xmlrpc.call('get_medias', modules_list)
    if err:
        return err
    else:
        medias = result
        if medias:
            # check if we need authentication
            auths = Set()
            for media in medias:
                if 'auth' in media and media['auth']:
                    auths.add(media['auth'])
            if auths:
                return render_to_response('media_auth.html',
                    {'auths': auths}, context_instance=RequestContext(request))
            else:
                return render_to_response('media_add.html',
                    {'medias': medias}, context_instance=RequestContext(request))
        else:
            return HttpResponseRedirect(reverse('install'))

@login_required
def medias_add(request):
    """ media add page """
    modules_list = request.session['modules_list']
    err, result = xmlrpc.call('get_medias', modules_list)
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
            {'medias': medias}, context_instance=RequestContext(request))

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
    # launch modules install
    err, result = xmlrpc.call('install_modules', request.session['modules_list'])
    if err:
        return err
    else:
        if result:
            return render_to_response('install.html',
                {'modules': request.session['modules']},
                context_instance=RequestContext(request))
        else:
            return HttpResponseRedirect(reverse('config'))

@login_required
def reload_packages(request):
    err, result = xmlrpc.call('load_packages')
    return HttpResponse("")

@login_required
def config(request):
    """ configuration page """
    modules = request.session['modules']
    modules_list = request.session['modules_list']
    err, result = xmlrpc.call('get_config', modules_list)
    if err:
        return err
    else:
        config = result
    # check if the modules needs configuration
    do_config = False
    # check if the modules have configuration scripts
    skip_config = True
    for m1 in config:
        for m2 in modules:
            if m1[0]['id'] == m2['id']:
                if m1[0].get('do_config'):
                    do_config = True
                if not m1[0].get('skip_config'):
                    skip_config = False
                # store in the module list skip_config
                # information for config_run view
                m2['skip_config'] = m1[0].get('skip_config')
    request.session['modules'] = modules

    # all modules does'nt have a configuration script
    if skip_config:
        for module in modules_list:
            config_end(request, module)
        return render_to_response('config_no.html',
            {'modules': modules},
            context_instance=RequestContext(request));
    # some module have a configuration
    elif do_config:
        return render_to_response('config.html',
            {'config': config, 'modules': modules},
            context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('config_valid'))

@login_required
def config_valid(request):
    """ check user configuration """
    modules = request.session['modules']
    modules_list = request.session['modules_list']
    # get forms values
    config = {}
    for name, value in request.POST.items():
        config[name] = value
    # validate values
    err, result = xmlrpc.call('valid_config', modules_list, config)
    if err:
        return err
    else:
        errors = result[0]
        config = result[1]
    if errors:
        return render_to_response('config.html',
            {'config': config, 'modules': modules},
            context_instance=RequestContext(request))
    else:
        return render_to_response('config_run.html',
            {'config': config, 'modules': modules, 'mode': 'start'},
            context_instance=RequestContext(request))

@login_required
def config_start(request):
    """ contiguration start page """
    modules = request.session['modules']
    return render_to_response('config_run.html',
        {'modules': modules, 'mode': 'run' },
        context_instance=RequestContext(request))

@login_required
def config_run(request, module):
    """ run configuration script for module """
    err, result = xmlrpc.call('run_config', module)
    if result:
        return HttpResponse("")
    else:
        raise Http404

@login_required
def config_end(request, module):
    """ tells the agent the module has been configured """
    err, result = xmlrpc.call('end_config', module)
    return HttpResponse("")


def toHtml(request, text):
    # replace hostname tag with server name
    text = re.sub('@HOSTNAME@', request.META['HTTP_HOST'].replace(':8000', ''), text);
    # new line replacement
    text = re.sub('@BR@', '<br/>', text);
    # bold support
    text = re.sub(r'@B@(.*)@B@', r'<strong>\1</strong>', text);
    # make links
    text = re.sub(r'(https?:\/\/[^ <)]*)', r'<a href="\1">\1</a>', text);
    return text
