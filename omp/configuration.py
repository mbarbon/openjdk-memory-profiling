import sys

if sys.version_info.major >= 3:
    import configparser
else:
    import ConfigParser as configparser

class Configuration(object):
    def __init__(self, path=None):
        self.jdk = (None, None, None)
        self.bits = None
        if path:
            self.read(path)

    def jdk_version(self):
        return self.jdk[0]

    def jdk_directory(self):
        return self.jdk[0] + 'u'

    def read(self, path):
        conf = configparser.ConfigParser()
        conf.read(path)
        self.jdk = (
            conf.get('jdk', 'jdk_version'),
            conf.getint('jdk', 'jdk_update'),
            conf.getint('jdk', 'jdk_build'),
        )
        self.bits = conf.getint('jdk', 'bits')

    def write(self, path):
        conf = configparser.ConfigParser()
        conf.add_section('jdk')
        conf.set('jdk', 'jdk_version', self.jdk[0])
        conf.set('jdk', 'jdk_update', str(self.jdk[1]))
        conf.set('jdk', 'jdk_build', str(self.jdk[2]))
        conf.set('jdk', 'bits', str(self.bits))
        with open(path, 'w') as out:
            conf.write(out)
