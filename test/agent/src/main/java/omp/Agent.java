package omp;

public class Agent {
    public native static void start(int sampleSize);

    public native static void stop();

    public native static long getCounter();

    public native static long getStoppedCounter();

    public native static void resetCounters();
}
