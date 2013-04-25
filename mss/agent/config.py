import os
import ConfigParser
import traceback

from mss.agent.lib.utils import Singleton


def check_path(path):
    if not os.path.exists(path):
        raise Exception("Path %s doesn't exists" % path)
    return path


class Config(object):
    __metaclass__ = Singleton

    DEFAULTS = [
        ("agent", "host", "127.0.0.1"),
        ("agent", "port", 8001, int),
        ("agent", "log_file", "/var/log/mss/mss-agent.log"),
        ("agent", "db_file", "/var/lib/mss/mss-agent.db"),
        ("local", "baseDir", "/var/lib/mss", check_path),
        ("local", "localDir", "/var/lib/mss/local", check_path),
        ("local", "cacheDir", "/var/lib/mss/cache", check_path),
        ("local", "cache", 1, int),
        ("api", "baseUrl", "https://serviceplace.mandriva.com/api/v1"),
        ("api", "sectionsUrl", "https://serviceplace.mandriva.com/api/v1/sections/mbs/1.0/"),
        ("api", "addonsUrl", "https://serviceplace.mandriva.com/api/v1/addons/mbs/1.0/"),
        ("api", "tokenUrl", "https://serviceplace.mandriva.com/api/v1/token/")
    ]

    def __init__(self, config_path):
        print "Using configuration %s" % config_path
        self.config = ConfigParser.ConfigParser();
        try:
            self.config.readfp(open(config_path))
        except IOError:
            print "Error while reading configuration at %s" % config_path
            print traceback.format_exc()
            raise

    def __getattr__(self, attr):
        option = None
        for d in self.DEFAULTS:
            if d[1] == attr:
                option = d
                break

        if option is not None:
            try:
                value = self.config.get(option[0], option[1])
                if len(option) > 3:
                    conv = option[3]
                    value = conv(value)
                return value
            except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                return option[2]
            except Exception:
                print "Failed to read option %s, using default: %s"  % (option[1], option[2])
                print traceback.format_exc()
                return option[2]
        else:
            return self.__getattr__(attr)
