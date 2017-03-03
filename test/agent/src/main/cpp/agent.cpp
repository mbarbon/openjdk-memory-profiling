#include "omp_Agent.h"

#include <jvmti.h>
#include <dlfcn.h>

static const jlong LONG_SAMPLE = sizeof(ssize_t) == 8 ?
    0x007fffffffffffff :
            0x7fffffff;

typedef void (*MemTrack_userCallback)(jlong samples);
typedef void (*MemTrack_setUserCallback_t)(MemTrack_userCallback callback, jlong sampleSize);

static MemTrack_setUserCallback_t MemTrack_setUserCallback;
static jlong sampleCounter, stoppedSampleCounter;

static void recordSample(jlong samples) {
    sampleCounter += samples;
}

static void recordStoppedSample(jlong samples) {
    stoppedSampleCounter += samples;
}

JNIEXPORT jint JNICALL Agent_OnLoad(JavaVM *jvm, char *options, void *reserved) {
    void *callback = dlsym(RTLD_DEFAULT, "MemTrack_setUserCallback");
    if (!callback) {
        fprintf(stderr, "Unable to find symbol for 'MemTrack_setUserCallback'");

        return JNI_ERR;
    }

    MemTrack_setUserCallback = (MemTrack_setUserCallback_t) callback;
    MemTrack_setUserCallback(recordStoppedSample, LONG_SAMPLE);

    return JNI_OK;
}

JNIEXPORT void JNICALL Java_omp_Agent_start(JNIEnv *, jclass, jint sampleSize) {
    MemTrack_setUserCallback(recordSample, sampleSize);
}

JNIEXPORT void JNICALL Java_omp_Agent_stop(JNIEnv *, jclass) {
    MemTrack_setUserCallback(recordStoppedSample, LONG_SAMPLE);
}

JNIEXPORT jlong JNICALL Java_omp_Agent_getCounter(JNIEnv *, jclass) {
    return sampleCounter;
}

JNIEXPORT jlong JNICALL Java_omp_Agent_getStoppedCounter(JNIEnv *, jclass) {
    return stoppedSampleCounter;
}

JNIEXPORT void JNICALL Java_omp_Agent_resetCounter(JNIEnv *, jclass) {
    sampleCounter = 0;
}
