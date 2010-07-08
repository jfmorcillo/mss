import traceback
import sys
import ConfigParser
import re
import os

def formatExceptionInfo(maxTBlevel=5):
    cla, exc, trbk = sys.exc_info()
    excName = cla.__name__
    try:
        excArgs = exc.__dict__["args"]
    except KeyError:
        excArgs = "<no args>"
    excTb = traceback.format_tb(trbk, maxTBlevel)
    return str(excName+" "+excArgs+" : \n"+excTb[0])

def getINIoption(section, option, ini):
    config = ConfigParser.SafeConfigParser()
    config.read(ini)
    return config.get(section, option)

def grep(search, file):
    if os.path.exists(file):
        h = open(file)
        string = h.read()
        h.close()
        expr = re.compile(search, re.M)
        if expr.search(string):
            return True
        else:
            return False
    else:
        return False
