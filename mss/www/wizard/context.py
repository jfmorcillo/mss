from mss.www.wizard.xmlrpc import XmlRpc

xmlrpc = XmlRpc()

def mes_media(request):
    err, result = xmlrpc.call("check_media", "download\.mandriva\.com\/EnterpriseServer")
    if err:
        return {'mes_media': 'err'}
    else:
        return {'mes_media': result}
        
def current_lang(request):
    from django.conf import settings
    return {'current_lang': settings.DEFAULT_LANGUAGE}
