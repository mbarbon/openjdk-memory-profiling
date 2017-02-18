package omp;

import java.util.Arrays;
import java.util.List;

public class EscapeTest {
    private static final List<Integer> testList = Arrays.asList(
        1, 2, 3
    );

    private static int iteration() {
        int c = 0;
        for (int i : testList)
            c += i;
        return c;
    }

    public static void main(String[] args) throws InterruptedException {
        int iterations = Integer.parseInt(args[0]);
        int dummyCounter = 0;

        // heuristic, should be enough for C2 JIT to kick in
        for (int i = 0; i < 20000; ++i)
            dummyCounter += iteration();
        Thread.sleep(2000);

        Agent.start(1);

        for (int i = 0; i < iterations; ++i)
            dummyCounter += iteration();

        Agent.stop();

        System.out.println("dummyCounter: " + dummyCounter);
        System.out.println("memorySamples: " + Agent.getCounter());
        System.out.println("stoppedMemorySamples: " + Agent.getStoppedCounter());
    }
}
