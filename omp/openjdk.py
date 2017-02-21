import glob
import os

class OpenJDK(object):
    JVM_INTERPRETER = ['-Xint']
    JVM_C1 = ['-XX:TieredStopAtLevel=1']
    JVM_C2 = []
    JVM_C2_NOESCAPE = ['-XX:-DoEscapeAnalysis']

    def __init__(self, conf):
        self.conf = conf
        self.java_home = None
        self.java_executable = None

    def find_jdk_build_directory(self):
        if self.java_executable:
            return

        potential = glob.glob('%s/build/*/jdk' % self.conf.jdk_directory())
        if len(potential) == 0:
            raise Exception("Couldn't find JDK build directory in '%s'" %
                                self.conf.jdk_directory())
        if len(potential) > 1:
            raise Exception("Multiple JDK build directories in '%s'" %
                                self.conf.jdk_directory())
        self.java_home = os.path.abspath(potential[0])
        self.java_executable = os.path.join(potential[0], 'bin', 'java')

    def with_java_home(self, orig=os.environ):
        dict_copy = orig.copy()
        dict_copy['JAVA_HOME'] = self.java_home
        return dict_copy
