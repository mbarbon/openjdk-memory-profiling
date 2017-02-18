package omp;

public class SanityTest {
    private static int[] value;

    private static int iteration() {
        int c = 0;
        for (int i : value)
            c += i;
        return c;
    }

    public static void main(String[] args) throws InterruptedException {
        int iterations = Integer.parseInt(args[0]);
        int arraySize = Integer.parseInt(args[1]);
        int samplingSize = Integer.parseInt(args[2]);
        int dummyCounter = 0;

        // heuristic, should be enough for C2 JIT to kick in
        for (int i = 0; i < 20000; ++i) {
            value = new int[arraySize];
            dummyCounter += iteration();
        }
        Thread.sleep(2000);

        Agent.start(samplingSize);

        for (int i = 0; i < iterations; ++i) {
            value = new int[arraySize];
            dummyCounter += iteration();
        }

        Agent.stop();

        System.out.println("dummyCounter: " + dummyCounter);
        System.out.println("memorySamples: " + Agent.getCounter());
        System.out.println("stoppedMemorySamples: " + Agent.getStoppedCounter());
    }
}
