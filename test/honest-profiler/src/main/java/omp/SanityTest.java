package omp;

import com.insightfullogic.honest_profiler.core.control.Agent;

public class SanityTest {
    private static int[] value;

    private static int iteration() {
        int c = 0;
        for (int i : value)
            c += i;
        return c;
    }

    public static void main(String[] args) throws InterruptedException {
        if (Agent.getMemorySamplingSize() == 0)
            throw new IllegalStateException("Agent is not configured for memory profiling");
        if (Agent.isRunning())
            throw new IllegalStateException("Agent is already running");

        int dummyCounter = 0;

        Agent.setMemorySamplingSize(1);
        Agent.start();
        Thread.sleep(2000);

        for (int i = 0; i < 1000; ++i) {
            value = new int[100];
            dummyCounter += iteration();
        }

        Agent.stop();

        Agent.setMemorySamplingSize(512);
        Agent.start();
        Thread.sleep(2000);

        for (int i = 0; i < 1000; ++i) {
            value = new int[100];
            dummyCounter += iteration();
        }

        Agent.stop();

        System.out.println(dummyCounter);
    }
}
