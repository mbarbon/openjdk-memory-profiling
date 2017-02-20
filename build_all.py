#!/usr/bin/env python

import os
import subprocess
import sys

def _configure_openjdk(jdkdir, cc, cxx, bits=64):
    subprocess.check_call(['sh', './configure', '--with-target-bits=%s' % bits, 'CC=%s' % cc, 'CXX=%s' % cxx], cwd=jdkdir)

def build_openjdk(jdkdir):
    _configure_openjdk(jdkdir, 'gcc-5', 'g++-5')
    subprocess.check_call(['make', 'clean'], cwd=jdkdir)
    subprocess.check_call(['make', 'EXTRA_CFLAGS=-Wno-error'], cwd=jdkdir)

def build_honest_profiler(jdk_java_home):
    merged_env = os.environ.copy()
    merged_env['JAVA_HOME'] = jdk_java_home

    subprocess.check_call(['cmake', '.'], cwd='honest-profiler', env=merged_env)
    subprocess.check_call(['mvn', 'package', '-DskipTests=true'], cwd='honest-profiler')

if __name__ == '__main__':
    build_openjdk('jdk8u')
    build_honest_profiler('../jdk8u/build/linux-x86_64-normal-server-release/jdk')
    sys.exit(0)
