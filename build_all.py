#!/usr/bin/env python

import os
import subprocess
import sys

import omp

def _configure_openjdk(jdkdir, cc, cxx, bits=64):
    subprocess.check_call(['sh', './configure', '--with-target-bits=%s' % bits, 'CC=%s' % cc, 'CXX=%s' % cxx], cwd=jdkdir)

def build_openjdk(conf):
    jdkdir = conf.jdk_directory()
    _configure_openjdk(jdkdir, 'gcc-5', 'g++-5', conf.bits)
    subprocess.check_call(['make', 'clean'], cwd=jdkdir)
    subprocess.check_call(['make', 'EXTRA_CFLAGS=-Wno-error'], cwd=jdkdir)

def build_honest_profiler(ojdk):
    ojdk.find_jdk_build_directory()

    subprocess.check_call(['cmake', '.'], cwd='honest-profiler', env=ojdk.with_java_home())
    subprocess.check_call(['mvn', 'package', '-DskipTests=true'], cwd='honest-profiler')

def build_tests(ojdk):
    subprocess.check_call(['mvn', 'package', '-DskipTests=true'], cwd='test')

if __name__ == '__main__':
    conf = omp.configuration.Configuration('configuration.ini')
    ojdk = omp.openjdk.OpenJDK(conf)

    build_openjdk(conf)
    build_honest_profiler(ojdk)
    build_tests(ojdk)
    sys.exit(0)
