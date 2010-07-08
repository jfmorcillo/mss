import urllib

class Media:

    def __init__(self, name, verbose_name, urls, auth=None, proto="https", mode="default"):
        self.name = name
        self.verbose_name = verbose_name
        self.auth = auth
        self.urls = urls
        self.proto = proto
        self.mode = mode
        
    def need_auth(self):
        if self.auth:
            return True
        else:
            return False
            
    def get_commands(self, login=None, password=None):
    
        commands = []    
        self.options = []
        
        if self.mode == "distrib":
            self.options.append('--distrib')
        elif self.mode == "updates":
            self.options.append('--updates')
        elif self.mode == "distrib_updates":
            self.options.append('--updates')            
            self.options.append('--distrib')
        else:
            self.options.append(self.name)
            
        for url in self.urls:
            if login and password:
                command = ['urpmi.addmedia'] + self.options + [ self.proto+"://"+urllib.quote(login)+":"+password+"@"+url ]
            else:
                command = ['urpmi.addmedia'] + self.options + [ self.proto+"://"+url ]
            commands.append(command)
            
        return commands
