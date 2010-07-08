# -*- coding: UTF-8 -*-

import xmlrpclib
from datetime import datetime
import re
import time

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

from config import ConfigManager
from xmlrpc import XmlRpc

xmlrpc = XmlRpc()
CM = ConfigManager()
output = {"status": "", "install": "", "config": ""}

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
    # check root user
    try:
        User.objects.get(username="root")
    except ObjectDoesNotExist:
        return direct_to_template(request, 'first_time.html')
    else:
        return HttpResponseRedirect(reverse('login_form'))

def login_form(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('sections'))
    else:
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
    MAX_TIME = 10
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

@login_required
def sections(request):
    """ sections list """
    # render the main page with all sections
    return render_to_response('sections.html',
        {'sections': CM.get_sections()}, 
        context_instance=RequestContext(request))

@login_required
def section(request, section):
    """ render section page """
    # flush some user session data
    for key in ('modules', 'modules_list', 'medias_auths', 'media_tpl'):
        try:
            del request.session[key]
        except KeyError:
            pass
    # get section name
    section_name = CM.get_section_name(section)
    # get detailled section info
    section_info = CM.get_section(section)
    # get modules list for section
    section_modules = CM.get_section_modules(section)
    # get modules info for modules list
    err, result = xmlrpc.call('get_modules', section_modules)
    if err:
        return err
    else:
        # detailed modules list
        modules = result
        # create simple modules list
        modules_list = [m.get('id') for m in modules]
        # remove modules not present server side
        for section in section_info:
            for module in section['modules']:
                if module not in modules_list:
                    section['modules'].remove(module)

        return render_to_response('section.html',
            {'section_name': section_name, 'section': section_info, 
            'modules': modules},
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

"""
[
    [{'auth': 'my', 'name': 'GroupOffice', 'urls': ['dl.mandriva.com/mes5/addons/groupoffice/release', 'dl.mandriva.com/mes5/addons/groupoffice/updates'], 'proto': 'https'}],
    ['my'], 
    []
]
"""
@login_required
def medias(request):
    """ media page """
    if request.method == "POST":
        # single media add from form
        if request.POST.get('media_name'):
            # get media details from POST
            verbose_name = request.POST.get('media_verbose_name')
            name = request.POST.get('media_name')
            auth = request.POST.get('media_auth')
            url = request.POST.get('media_url')
            proto = request.POST.get('media_proto')
            mode = request.POST.get('media_mode')
                        
            if verbose_name and name and url and proto and mode:
            
                # create dict for media authentication form
                if auth:
                    auths = { auth: {'verbose_name': verbose_name, 'name': name, 
                        'urls': [ url ], 'proto': proto, 'mode': mode, 
                        'auth': auth}}
                # TODO
                else:
                    pass
                done = []
                request.session['medias_auths'] = auths
                # use single template (no head)
                request.session['medias_tpl'] = 'single'
                return render_to_response('medias_single.html',
                        {'auths': auths, 'done': done},
                        context_instance=RequestContext(request))
        # media add for modules list
        else:
            modules_list = request.session['modules_list']
            err, result = xmlrpc.call('get_medias', modules_list)
            if err:
                return err
            else:
                auths = result[0]
                done = result[1]
            request.session['medias_auths'] = auths
            request.session['medias_tpl'] = 'modules'
            if len(auths) > 0:
                return render_to_response('medias_modules.html',
                    {'auths': auths, 'done': done},
                    context_instance=RequestContext(request))
            elif len(done) > 0:
                return render_to_response('medias_modules_add.html',
                    {'done': done},
                    context_instance=RequestContext(request))
            else:
                return HttpResponseRedirect(reverse('install'))
    else:
        return HttpResponseRedirect(reverse('sections'))

@login_required
def add_medias(request):
    """ media auth page """
    if request.method == "POST":
        auths = request.session['medias_auths']
        tpl = request.session['medias_tpl']
        errors = False
        for auth, media in auths.items():
            login = request.POST.get(auth + "_login", "")
            passwd = request.POST.get(auth + "_passwd", "")
            print media
            err, result = xmlrpc.call("add_media", media, login, passwd)
            if err:
                return err
            else:
                print result
                done = result[0]
                fail = result[1]
            if len(fail) > 0:
                errors = True
        if not errors:
            return render_to_response('medias_'+tpl+'_add.html',
                {'done': done},
                context_instance=RequestContext(request))
        else:
            return render_to_response('medias_'+tpl+'.html',
                {'auths': auths, 'done': done, 'fail': fail}, 
                context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('sections'))

@login_required
def update_medias(request):
    err, result = xmlrpc.call('update_medias')
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
            return render_to_response('install_no.html',
                {'modules': request.session['modules']},
                context_instance=RequestContext(request))

@login_required
def install_state(request):
    """ install output page """
    err, result = xmlrpc.call('get_state', 'install')
    if err:
        return err
    else:
        code = result[0]
        output = result[1]
        str_output = ""
        for text_code, text in output:
            str_output += text+"\n"
    return render_to_response('install_log.html',
        {'code': code, 'output': str_output},
        context_instance=RequestContext(request))

@login_required
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
            return render_to_response('config_no.html',
                {'modules': modules},
                context_instance=RequestContext(request))            
        # some module have a configuration
        elif do_config:
            return render_to_response('config.html',
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
def config_state(request, module):
    """ config output page """
    err, result = xmlrpc.call('get_state', 'config', module)
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
    return render_to_response('config_log.html',
        {'code': code, 'output': output, 'infos': infos},
        context_instance=RequestContext(request))

@login_required
def config_end(request, module):
    err, result = xmlrpc.call('end_config', module)
    return HttpResponse("")


def toHtml(request, text):
    # replace hostname tag with server name
    text = re.sub('@HOSTNAME@', request.META['HTTP_HOST'].replace(':8000', ''), text);
    # make links
    text = re.sub(r'(http:\/\/[^ <)]*)', r'<a href="\1"><strong>\1</strong></a>', text);
    return text
