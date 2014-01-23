import ConfigParser
import os


class Settings(object):
    def __init__(self):
        self.config = ConfigParser.SafeConfigParser()
        settings_path = "%s/%s" % (os.path.dirname(os.path.abspath(__file__)),
                                   'settings.conf')
        settings_fp = open(settings_path)
        self.config.readfp(settings_fp)
        return

    def get(self, section, option, default=None):
        try:
            return self.config.get(section, option)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError):
            pass
        return default

settings = Settings()
