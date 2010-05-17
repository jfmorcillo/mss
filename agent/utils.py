import traceback
import sys
import ConfigParser

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
