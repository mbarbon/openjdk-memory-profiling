#!/usr/bin/env python

import glob
import subprocess
import sys

import omp

class OpenJDK(omp.openjdk.OpenJDK):
    TEST_AGENT_ARG = None
    HONEST_PROFILER_ARG = 'honest-profiler/build/liblagent.so=start=0,memorySampleSize=64,logPath=hp-log.hpl'
    TEST_AGENT_CLASSES = 'test/agent/target/test-agent-0.0.1.jar'
    HONEST_PROFILER_CLASSES = 'honest-profiler/target/honest-profiler.jar'
    TEST_HONEST_PROFILER_CLASSES = [
        HONEST_PROFILER_CLASSES,
        'test/honest-profiler/target/test-honest-profiler-0.0.1.jar',
    ]

    def find_test_agent(self):
        if self.TEST_AGENT_ARG:
            return

        potential = glob.glob('test/agent/target/nar/*/lib/*/jni/libtest-agent-0.0.1.so')
        if len(potential) != 1:
            raise Exception("Couldn't find test agent binary")
        self.TEST_AGENT_ARG = potential[0]

    def run_simple_test(self, java_class, extra_args=[], jvm_args=[]):
        self.find_jdk_build_directory()
        self.find_test_agent()

        out = subprocess.check_output([
                self.java_executable, '-cp', self.TEST_AGENT_CLASSES,
                '-agentpath:' + self.TEST_AGENT_ARG,
            ] + jvm_args + [java_class] + extra_args, env=ojdk.with_java_home())
        res = dict((k, v) for (k, v) in
                           [l.split(': ', 2)
                                for l in out.decode('ascii').split('\n') if l])
        if int(res.get('stoppedMemorySamples', -1)) != 0:
            raise Exception('We gathered samples while profiling was stopped: %d' % res.get('stoppedMemorySamples', -1))
        return res

    def run_honest_profiler_test(self, java_class, extra_args=[], jvm_args=[]):
        out = subprocess.check_output([
                self.java_executable, '-cp', ':'.join(self.TEST_HONEST_PROFILER_CLASSES),
                '-agentpath:' + self.HONEST_PROFILER_ARG,
            ] + jvm_args + [java_class] + extra_args, env=ojdk.with_java_home())
        return out

    def run_class(self, java_class, classpath, extra_args=[], jvm_args=[]):
        out = subprocess.check_output([
                self.java_executable, '-cp', ':'.join(classpath),
            ] + jvm_args + [java_class] + extra_args, env=ojdk.with_java_home())
        return out

def _run_sanity_test(ojdk, jvm_args):
    res1 = ojdk.run_simple_test('omp.SanityTest', extra_args=['1', '2', '1'], jvm_args=jvm_args)
    res2 = ojdk.run_simple_test('omp.SanityTest', extra_args=['1000', '2', '1'], jvm_args=jvm_args)
    res3 = ojdk.run_simple_test('omp.SanityTest', extra_args=['1', '100', '1'], jvm_args=jvm_args)
    res4 = ojdk.run_simple_test('omp.SanityTest', extra_args=['1000', '100', '1'], jvm_args=jvm_args)
    return [int(res.get('memorySamples')) for res in (res1, res2, res3, res4)]

def run_sanity_test(ojdk):
    interpreted = _run_sanity_test(ojdk, ojdk.JVM_INTERPRETER)
    c1 = _run_sanity_test(ojdk, ojdk.JVM_C1)
    c2_noescape = _run_sanity_test(ojdk, ojdk.JVM_C2_NOESCAPE)
    c2 = _run_sanity_test(ojdk, ojdk.JVM_C2)

    baseline = interpreted[0] - 16 - 4 * 2
    it_1000_size_1 = baseline + 1000 * (16 + 4 * 2)
    it_1_size_100 = baseline + 1 * (16 + 4 * 100)
    it_1000_size_100 = baseline + 1000 * (16 + 4 * 100)
    expected = [interpreted[0], it_1000_size_1, it_1_size_100, it_1000_size_100]

    def check(res, description):
        if res != expected:
            raise Exception('Unexpected result for %s: %s != %s' % (description, res, expected))

    check(interpreted, 'interpreted')
    check(c1, 'C1 JIT')
    check(c2_noescape, 'C2 JIT (no escape analysis)')
    check(c2, 'C2 JIT (with escape anaysis)')

def _run_escape_test(ojdk, iterations, jvm_args):
    res = ojdk.run_simple_test('omp.EscapeTest', extra_args=[iterations], jvm_args=jvm_args)
    return int(res.get('memorySamples'))

def run_escape_test(ojdk):
    c2_noescape = _run_escape_test(ojdk, '100000000', ojdk.JVM_C2_NOESCAPE)
    c2 = _run_escape_test(ojdk, '100000000', ojdk.JVM_C2)

    # 32 is the size of the iterator
    if int(c2_noescape / 100000000) != 32:
        raise Exception('Unexpected result for C2 JIT (no escape analysis): ratio %d != 32' % (c2_noescape / 100000000))
    # things still allocate memory even if the test loop does not: check
    # that we don't allocate that much
    if c2_noescape / c2 < 30:
        raise Exception('Unexpected result for C2 JIT (escape analysis): ratio %d is < 30' % (c2_noescape / c2))

def _run_sampling_test(ojdk, size, jvm_args):
    res = ojdk.run_simple_test('omp.SanityTest', extra_args=['1000', '100', size], jvm_args=jvm_args)
    return int(res.get('memorySamples'))

def run_sampling_test(ojdk):
    interpreted = _run_sampling_test(ojdk, '1', ojdk.JVM_INTERPRETER)
    interpreted_64 = _run_sampling_test(ojdk, '64', ojdk.JVM_INTERPRETER)
    c1 = _run_sampling_test(ojdk, '1', ojdk.JVM_C1)
    c1_64 = _run_sampling_test(ojdk, '64', ojdk.JVM_C1)
    c2_noescape = _run_sampling_test(ojdk, '1', ojdk.JVM_C2_NOESCAPE)
    c2_noescape_64 = _run_sampling_test(ojdk, '64', ojdk.JVM_C2_NOESCAPE)

    def check(res_1, res_64, description):
        if res_64 != int(res_1 / 64):
            raise Exception('Unexpected result for %s: %d != %d' % (description, res_64, res_1 / 64))

    check(interpreted, interpreted_64, 'interpreted')
    check(c1, c1_64, 'C1 JIT')
    check(c2_noescape, c2_noescape_64, 'C2 JIT (no escape analysis)')

def run_honest_profiler_test(ojdk):
    ojdk.run_honest_profiler_test('omp.SanityTest')

    traces = ojdk.run_class('omp.TraceDumper', ojdk.TEST_HONEST_PROFILER_CLASSES, extra_args=['hp-log.hpl'])
    main_traces = [line for line in traces.decode('ascii').split('\n')
                       if line.startswith('omp.SanityTest.main:')]
    trace_map = dict(line.split(' ') for line in main_traces)

    sample_1 = int(trace_map.get('omp.SanityTest.main:28'))
    sample_512 = int(trace_map.get('omp.SanityTest.main:39'))

    if sample_1 != 416000:
        raise Exception('Unexpected result: %d != 416000' % sample_1)
    if sample_512 != int(sample_1 / 512):
        raise Exception('Unexpected result: %d != %d' % (sample_512, sample_1 / 512))

if __name__ == '__main__':
    conf = omp.configuration.Configuration('configuration.ini')
    ojdk = OpenJDK(conf)
    print('Running OpenJDK-only tests...')

    print('    sanity test...')
    run_sanity_test(ojdk)
    print('    escape anaysis test...')
    run_escape_test(ojdk)
    print('    sampling size test...')
    run_sampling_test(ojdk)

    print('Running Honest-Profiler tests...')

    print('    sanity test...')
    run_honest_profiler_test(ojdk)

    sys.exit(0)
