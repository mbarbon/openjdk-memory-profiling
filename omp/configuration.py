import configparser

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
        conf_jdk = conf['jdk']
        self.jdk = (
            conf_jdk['jdk_version'],
            int(conf_jdk['jdk_update']),
            int(conf_jdk['jdk_build']),
        )
        self.bits = int(conf_jdk['bits'])

    def write(self, path):
        conf = configparser.ConfigParser()
        conf['jdk'] = {'jdk_version': self.jdk[0],
                       'jdk_update': self.jdk[1],
                       'jdk_build': self.jdk[2],
                       'bits': self.bits}
        with open(path, 'w') as out:
            conf.write(out)
