#!/usr/bin/env python

import glob
import os
import subprocess
import sys

patches = {
    ('jdk8', 112): 'memory-profiling-jdk8-u112',
    ('jdk8', 122): 'memory-profiling-jdk8-u112',
    ('jdk8', 152): 'memory-profiling-jdk8-u112',
}

HGRCPATH = ':'.join([
    os.path.abspath('jdk-hgrc'),
    os.path.expanduser('~/.hgrc'),
])

def _env(**kwargs):
    envcopy = os.environ.copy()
    envcopy.update(kwargs)

    return envcopy

def _hg(directory, command):
    print(' '.join(['hg'] + command))
    subprocess.check_output(['hg'] + command, cwd=directory, env=_env(HGRCPATH=HGRCPATH))

def _hgforest(directory, command):
    print(' '.join(['./common/bin/hgforest.sh'] + command))
    subprocess.check_output(['sh', './common/bin/hgforest.sh'] + command, cwd=directory, env=_env(HGRCPATH=HGRCPATH))

def _git(directory, command):
    print(' '.join(['git'] + command))
    subprocess.check_output(['git'] + command, cwd=directory)

def reset_openjdk(jdkv, jdku, jdkb):
    patch = patches.get((jdkv, jdku), None)
    if patch == None:
        raise Exception('No patch for %su%s' % (jdkv, jdku))
    base_revision = '%su%s-b%s' % (jdkv, jdku, jdkb)

    _hgforest('jdk8u', ['qpop', '-a'])
    _hgforest('jdk8u', ['update', '-r', base_revision, '-C'])
    _hgforest('jdk8u', ['purge'])
    _hg('jdk8u/hotspot', ['qpush', patch])
    if not os.path.exists('jdk8u/hotspot/.hg/patches'):
        os.path.symlink(os.path.abspath('hotspot-patches'),
                            'jdk8u/hotspot/.hg/patches')

def reset_honest_profiler(base_revision):
    _git('honest-profiler', ['reset', '--hard', base_revision])
    _git('honest-profiler', ['clean', '-X', '-d', '-f'])
    _git('honest-profiler', ['am'] + sorted(os.path.abspath(patch) for patch in glob.glob('honest-profiler-patches/*.patch')))

if __name__ == '__main__':
    reset_openjdk('jdk8', 112, 31)
    reset_honest_profiler('120e141aff9fada99fb6d423b512b6effae01a48')
    sys.exit(0)
