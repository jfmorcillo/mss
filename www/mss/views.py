# -*- coding: UTF-8 -*-

import xmlrpclib
from datetime import datetime
import re

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.simple import direct_to_template
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from config import get_sections, get_section, get_section_modules
from xmlrpc import XmlRpc

xmlrpc = XmlRpc()

def mylogin(request):
    if request.method == "POST":
        lang = request.POST.get('language', None)
        user = authenticate(username=request.POST['username'], 
            password=request.POST['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                # success
                response = HttpResponseRedirect(reverse('sections'))
                # set agent language
                err, result = xmlrpc.call('set_lang', lang)
                if err:
                    return err
                return response
        else:
            # disabled account
            return direct_to_template(request, 'inactive_account.html',
                extra_context = {'DEFAULT_LANGUAGE': settings.DEFAULT_LANGUAGE})
    else:
        # invalid login
        return direct_to_template(request, 'invalid_login.html',
            extra_context = {'DEFAULT_LANGUAGE': settings.DEFAULT_LANGUAGE})
      
def mylogout(request):
    logout(request)
    # reset language
    if hasattr(request, 'session'):
        request.session['django_language'] = settings.DEFAULT_LANGUAGE
    return HttpResponseRedirect(reverse('first_time'))

def first_time(request):
    # check root user
    try:
        User.objects.get(username="root")
    except ObjectDoesNotExist:
        return direct_to_template(request, 'mss/first_time.html',
            {'DEFAULT_LANGUAGE': settings.DEFAULT_LANGUAGE})
    else:
        return HttpResponseRedirect(reverse('login_form'))

def login_form(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('sections'))
    else:
        # set language
        if hasattr(request, 'session'):
            request.session['django_language'] = settings.DEFAULT_LANGUAGE
        return render_to_response('mss/login.html', 
            {'DEFAULT_LANGUAGE': settings.DEFAULT_LANGUAGE},
            context_instance=RequestContext(request))

def error(request, code):
    """ error page """
    return render_to_response('mss/error.html', {'code': code},
        context_instance=RequestContext(request))

@login_required
def sections(request):
    """ sections list """
    return render_to_response('mss/sections.html',
        {'sections': get_sections()}, 
        context_instance=RequestContext(request))

@login_required
def section(request, section):
    """ render section page """
    # flush user session data
    for key in ('modules', 'modules_list', 'medias_auth', 'medias_auth_types'):
        try:
            del request.session[key]
        except KeyError:
            pass
    section_info = get_section(section)
    # get modules list for section
    section_modules = get_section_modules(section)
    # get modules info for modules list
    err, result = xmlrpc.call('get_modules', section_modules)
    if err:
        return err
    else:
        modules = result
        modules_list = [m.get('id') for m in modules]
        # remove modules not present server side
        for section in section_info:
            for module in section['modules']:
                if module not in modules_list:
                    section['modules'].remove(module)

        return render_to_response('mss/section.html',
            {'section': section_info, 'modules': modules},
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
            return render_to_response('mss/preinst.html',
                {'modules': modules},
                context_instance=RequestContext(request))                
    else:
        return HttpResponseRedirect(reverse('sections'))

@login_required
def medias(request):
    """ media page """
    if request.method == "POST":
        modules_list = request.session['modules_list']
        err, result = xmlrpc.call('get_medias', modules_list)
        if err:
            return err
        else:
            auths = result[0]
            types = result[1]
            done = result[2]
        request.session['medias_auth_types'] = types
        request.session['medias_auth'] = auths
        if len(auths) > 0:
            return render_to_response('mss/medias.html',
                {'auth': auths, 'types': types, 'done': done},
                context_instance=RequestContext(request))
        else:
            return HttpResponseRedirect(reverse('install'))
    else:
        return HttpResponseRedirect(reverse('sections'))

@login_required
def add_medias(request):
    """ media auth page """
    if request.method == "POST":
        types = request.session['medias_auth_types']
        auths = request.session['medias_auth']
        errors = False
        for auth_type in types:
            login = request.POST.get(auth_type + "_login")
            passwd = request.POST.get(auth_type + "_passwd")
            for media in auths:
                if media["auth"] == auth_type:
                    err, result = xmlrpc.call("add_media", media,
                        login, passwd)
                    if err:
                        return err
                    else:
                        done = result[0]
                        fail = result[1]
                    if len(fail) > 0:
                        errors = True
        if not errors:
            return render_to_response('mss/medias_add.html',
                context_instance=RequestContext(request))
        else:
            print fail
            return render_to_response('mss/medias.html',
                {'auth': auths, 'types': types, 'done': done,
                'fail': fail}, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('sections'))

@login_required
def install(request):
    """ install page """
    # launch modules install
    err, result = xmlrpc.call('install_modules', request.session['modules_list'])
    if err:
        return err
    else:
        if result:
            return render_to_response('mss/install.html',
                {'modules': request.session['modules']},
                context_instance=RequestContext(request))
        else:
            return render_to_response('mss/install_no.html',
                {'modules': request.session['modules']},
                context_instance=RequestContext(request))

@login_required
def install_state(request):
    """ install output page """
    err, result = xmlrpc.call('get_state')
    if err:
        return err
    else:
        code = result[0]
        output = result[1]
        str_output = ""
        for text_code, text in output:
            str_output += text+"\n"
    return render_to_response('mss/install_log.html',
        {'code': code, 'output': str_output},
        context_instance=RequestContext(request))

def reload_packages(request):
    err, result = xmlrpc.call('load_packages')
    return HttpResponse("")

@login_required
def config(request):
    """ configuration page """
    if request.method == "POST":
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
            return render_to_response('mss/config_no.html',
                {'modules': modules},
                context_instance=RequestContext(request))            
        # some module have a configuration
        elif do_config:
            return render_to_response('mss/config.html',
                {'config': config, 'modules': modules},
                context_instance=RequestContext(request))
        else:
            return HttpResponseRedirect(reverse('config_valid'))
    else:
        return HttpResponseRedirect(reverse('sections'))

@login_required
def config_valid(request):
    """ check user configuration """
    modules = request.session['modules']
    modules_list = request.session['modules_list']
    # get forms values
    config = {}
    for name, value in request.POST.items():
        config[name] = value
    print config
    # validate values
    err, result = xmlrpc.call('valid_config', modules_list, config)
    if err:
        return err
    else:
        errors = result[0]
        config = result[1]
    if errors:
        return render_to_response('mss/config.html',
            {'config': config, 'modules': modules},
            context_instance=RequestContext(request))
    else:
        return render_to_response('mss/config_run.html',
            {'config': config, 'modules': modules, 'mode': 'start'},
            context_instance=RequestContext(request))

@login_required  
def config_start(request):
    """ contiguration start page """
    modules = request.session['modules']
    return render_to_response('mss/config_run.html',
        {'modules': modules, 'mode': 'run' },
        context_instance=RequestContext(request))

@login_required
def config_run(request, module):
    """ run configuration script for module """
    err, result = xmlrpc.call('run_config', module)
    return HttpResponse("")

@login_required          
def config_state(request, module):
    """ config output page """
    err, result = xmlrpc.call('get_state', module)
    if err:
        return err
    else:
        code = result[0]
        output = result[1]
        infos = {"errors": [], "warnings": [], "summary": []}
        if code != 2000:
            for text_code, line in output:
                line = toHtml(request, line)
                if text_code == "1":
                    infos['warnings'].append(line)
                elif text_code == "2":
                    infos['errors'].append(line)
                elif text_code == "7":
                    infos['summary'].append(line)
                elif text_code == "8":
                    infos['summary'].append("<strong>"+line+"</strong>")
    return render_to_response('mss/config_log.html',
        {'code': code, 'output': output, 'infos': infos},
        context_instance=RequestContext(request))

def config_end(request, module):
    err, result = xmlrpc.call('end_config', module)
    return HttpResponse("")


def toHtml(request, text):
    # replace hostname tag with server name
    text = re.sub('@HOSTNAME@', request.META['HTTP_HOST'].replace(':8000', ''), text);
    # make links
    text = re.sub(r'(http:\/\/[^ <)]*)', r'<a href="\1"><strong>\1</strong></a>', text);
    return text
