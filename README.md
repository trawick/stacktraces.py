# stacktraces.py
## Python-based stack trace analysis tools

Stack traces (backtraces) can be obtained from the following:

1. live process or core file via gdb or Solaris pstack
2. log file containing Python stack traces

The software builds a representation of the available data which can be output as JSON or as text.  
Simple annotations can be applied based on pattern matching.

## Possible uses

* provide description of thread state in a snapshot of a process
* extract exceptions from log file and label in a way that indicates whether they are known issues or new ones
