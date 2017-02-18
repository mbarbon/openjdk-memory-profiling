package omp;

import com.insightfullogic.honest_profiler.core.parser.Method;
import com.insightfullogic.honest_profiler.core.parser.StackFrame;
import com.insightfullogic.honest_profiler.core.parser.ThreadMeta;
import com.insightfullogic.honest_profiler.core.parser.TraceStart;
import com.insightfullogic.honest_profiler.core.sources.LogSource;
import com.insightfullogic.honest_profiler.ports.javafx.Rendering;
import com.insightfullogic.honest_profiler.ports.sources.FileLogSource;
import com.insightfullogic.honest_profiler.core.Monitor;
import com.insightfullogic.honest_profiler.core.parser.LogEventListener;

import java.io.*;
import java.util.*;
import java.util.stream.Collectors;

public class TraceDumper {
    private static class TraceCollector implements LogEventListener {
        private final Map<List<StackFrame>, Long> traces = new HashMap<>();
        private final Map<Long, Method> methods = new HashMap<>();
        private List<StackFrame> currentTrace;
        private long currentSamples;

        @Override
        public void handle(TraceStart traceStart) {
            addCurrentTrace();
            currentTrace = new ArrayList<>();
            currentSamples = traceStart.getSamples();
        }

        @Override
        public void handle(StackFrame stackFrame) {
            currentTrace.add(stackFrame);
        }

        @Override
        public void handle(Method newMethod) {
            methods.put(newMethod.getMethodId(), newMethod);
        }

        @Override
        public void handle(ThreadMeta newThreadMeta) {
        }

        @Override
        public void endOfLog() {
            addCurrentTrace();
        }

        public Map<List<StackFrame>, Long> getTraceMap() {
            return traces;
        }

        public Method getMethod(long methodId) {
            return methods.get(methodId);
        }

        private void addCurrentTrace() {
            if (currentTrace == null)
                return;

            traces.compute(currentTrace, (k, v) -> (v == null ? 0 : v) + currentSamples);
        }
    }

    public static void main(String[] args) {
        String in = args[0];
        LogSource source = new FileLogSource(new File(in));
        TraceCollector collector = new TraceCollector();

        Monitor.consumeFile(source, collector);

        collector.getTraceMap().forEach((frames, samples) -> {
            ;
            boolean first = true;
            for (StackFrame frame : frames) {
                if (!first)
                    System.out.print(";");
                first = false;

                Method method = collector.getMethod(frame.getMethodId());
                if (method == null)
                    System.out.print("UNKNOWN");
                else
                    System.out.print(method.getClassName() + "." + method.getMethodName());
                System.out.print(":");
                System.out.print(frame.getLineNumber());
            }
            System.out.print(" ");
            System.out.println(samples);
        });
    }
}
