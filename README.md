# Accurate memory profiling for OpenJDK

**TL;DR** low-overhead profiler, takes escape analysis into account,
requires an OpenJDK patch

## Why this is useful

There are many tools (commercial and open source) that can help
investigate Java heap usage. There is a very specific combination of
feature that I miss:

- free for use in production
- low overhead
- takes into account escape analysis

Java Flight Recorder is low overhead and takes into account escape
analysis, but it's not free for production use. Other memory profilers
are high overhead and can't take into account escape analysis.

DTrace/SystemTap comes close, I only miss the ability of specifying a
sampling size, to tune the overhead.

## Escape analysis in brief

Consider this contrived example:

```java
    private static final List<Integer> someList = Arrays.asList(...);

    private static int doSomething() {
        int j = 0;
        for (int i : someList)
            j += i;
        return j;
    }
```

the `for()` loop allocates a new `Iterator<Integer>`, so we could
expect each call to `doSomething()` to allocate a small amount of
memory.

This is not always the case, because HotSpot (and other JVMs) detect
that the iterator never escapes the scope of the function and
therefore does not need to be allocated on the Java heap.

Unfortunatley there is no public interface to determine which
allocations have been removed by this optimization. Bytecode
instrumentation does not help: it allows to know that `new` was
called, but not whether the object was allocated on the heap or the
stack (also, the instrumentation bytecode interferes with escape
analysis).

A much more complete explanation can be found at [The Escape of ArrayList.iterator()](http://psy-lob-saw.blogspot.com/2014/12/the-escape-of-arraylistiterator.html).

## What this patch provides

The OpenJDK patch adds a C function taking as parameters the sampling
size (in bytes) and a callback function. On each allocation a counter
is increased by the amount of allocated memory, and when the total
exceeds the sampling size the callback is called and the counter is
reset.

The Honest Profiler patch adds memory profiling support by using this
new function.

Only works on x86 for now. Adding support for other architectures is
possible, but not a priority.

## Alternatives

Use Java Flight Recorder.

Use SystemTap/DTrace.

Use one of the other profilers, always keeping in mind that the result
can be misleading. There is no convenient way to cross-check whether
any of the recorded allocations will be escape-analyzed away during a
non-profiling run.

Hope for http://openjdk.java.net/jeps/8171119 to be implemented soon
(it's a superset of what this patch provides, and wrapped in a good
API).
