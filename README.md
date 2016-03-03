# stacktraces.py
## Python-based stack trace analysis library and command-line tools

Stack traces (backtraces) can be obtained from the following:

1. live process or core file via gdb or Solaris pstack
2. log file containing Python stack traces

The software builds a representation of the available data which can be output as JSON or as text.  
Simple annotations can be applied based on pattern matching.

## Possible uses

* provide description of thread state in a snapshot of a process
* extract exceptions from log file and label in a way that indicates whether they are known issues or new ones

<https://stacktraces.io/> uses this library for parsing stacktraces.

## Library

The API is in flux.  Read the command-line tool source code for hints.

## Installation

``collect.py`` can be downloaded individually and copied to the system where it is needed.  For the other tools, use ``pip install`` referencing a particular commit (e.g., ``git+git://github.com/trawick/stacktraces.py.git@XXXXXXX#egg=stacktraces``, where the Xs are replaced with an actual hash).

## Bug reports

Please file Github issues if you encounter a problem and you can share the text (e.g., Python exception, gdb output) that 
couldn't be parsed or represented properly as part of the problem description.  Sometimes problems will be encountered
dealing with proprietary data  which you can't share publicly; try to reproduce those with code you can share.
To be clear:  Communicate with me about questions and problems only via the Github issue tracker unless you want to
reimburse me for my time at a professional rate.

## Command-line tool documentation

### ``collect.py``

``collect.py`` invokes ``gdb`` or ``Solaris pstack`` to extract process and thread data and thread stacktraces from a live process or core file.  It is completely standalone, requiring only libraries bundled with Python 2.6 or later, so it can be copied by itself to the target system for use.

Here is a set of httpd processes and an invocation of ``collect.py`` to extract information from them:

```
 3469  2006 /home/trawick/inst/24-64/bin/httpd -k start
 5314  3469 /home/trawick/inst/24-64/bin/httpd -k start
 5315  3469 /home/trawick/inst/24-64/bin/httpd -k start
 5316  3469 /home/trawick/inst/24-64/bin/httpd -k start
 $ ./collect.py -p 5315 -e $HOME/inst/24-64-bin/httpd -l outfile
 $ head outfile 
REM collect.py 1.01 TOOL=gdb  PYPLATFORM=linux2 ./collect.py -p 5315 -e /home/trawick/inst/24-64-bin/httpd -l outfile
/home/trawick/inst/24-64-bin/httpd: No such file or directory.
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".
0x00007fa5fbf89870 in __poll_nocancel () at ../sysdeps/unix/syscall-template.S:81
81	../sysdeps/unix/syscall-template.S: No such file or directory.
From                To                  Syms Read   Shared Object Library
0x00007fa5fcb0f600  0x00007fa5fcb5dfc6  Yes (*)     /lib/x86_64-linux-gnu/libpcre.so.3
0x00007fa5fc8e3fe0  0x00007fa5fc905b2f  Yes         /home/trawick/inst/apr15-64/lib/libaprutil-1.so.0
0x00007fa5fc6b5b90  0x00007fa5fc6cde39  Yes (*)     /lib/x86_64-linux-gnu/libexpat.so.1
```

The output file can be used as-is (essentially automated invocation of the debugger) or fed to ``describe.py``.

### ``describe.py``

``describe.py`` can parse the output from ``collect.py`` (or other suitable ``gdb`` or ``pstack`` output) and render a simplified description.  It can usually give a synopsis of thread state and activity when used with ``httpd`` processes.

Here is sample output on an ``httpd`` process that it doesn't know anything about (mod_fcgid's daemon process):

```
$ ./describe.py --debuglog outfile 
Pid 5315 Executable /home/trawick/inst/24-64-bin/httpd 
1 * [1]
  __poll_nocancel, apr_wait_for_io_or_timeout, procmgr_fetch_cmd, pm_main, create_process_manager, procmgr_post_config, fcgid_init, ap_run_post_config, main,
```

Here is an example where it understands more about what is going on:

```
$ ./describe.py --debuglog outfile2
Pid 5316 Executable /home/trawick/inst/24-64-bin/httpd 
20 * [22] MPM child worker thread (waiting for connection to handle)
  apr_thread_cond_wait, ap_queue_pop, worker_thread, dummy_worker, 
1 * [2] MPM child listener thread (waiting for connection to accept)
  apr_pollset_poll, listener_thread, dummy_worker, 
1 * [1] MPM child main thread (waiting for termination event)
  read, ap_mpm_podx_check, child_main, make_child, startup_children, worker_run, ap_run_mpm, main,
```

In this case there are 20 threads with one stacktrace and description (MPM child worker thread) and two other threads
with different purposes (MPM child listener thread and MPM child main thread).

### ``describe_python_log.py``

``describe_python_log.py`` parses log files which contain Python exceptions, creating either plain text or JSON output describing those exceptions.  JSON output is suitable for importing into <https://stacktraces.io/> or for other kinds of analysis.

Example run with text output:
```
$ ./describe_python_log.py ~/walking.log 
TypeError: argument of type 'NoneType' is not iterable
get_response, process_exception, redirect, resolve_url

TypeError: string indices must be integers
get_response, _wrapped_view, index, weather_forecast, around

TypeError: a float is required
get_response, _wrapped_view, index, weather_forecast

error: [Errno 110] Connection timed out
get_response, _wrapped_view, index, weather_forecast, around, _fetch, request, _send_request, endheaders, _send_output, send, connect, create_connection

ConnectTimeout: HTTPConnectionPool(host='api.openweathermap.org', port=80): Max retries exceeded with url: /data/2.5/forecast?lat=35.88&lon=-78.75&mode=json&cnt=1 (Caused by ConnectTimeoutError(<requests.packages.urllib3.connection.HTTPConnection object at 0xad7cbf2c>, 'Connection to api.openweathermap.org timed out. (connect timeout=10.0)'))
_fetch, get, request, request, send, send

...

Duplicated error messages:
  82: ValueError: No JSON object could be decoded
  2: IntegrityError: duplicate key value violates unique constraint "walks_walk_walk_group_id_key"|DETAIL:  Key (walk_group_id, walk_datetime)=(ExYu, 2016-01-10 14:30:00+00) already exists.
  2: ValueError: Extra data: line 2 column 1 - line 3 column 1 (char 4 - 67)
  15: TypeError: string indices must be integers
  ...
Duplicated stacktraces:
  15: get_response, _wrapped_view, index, weather_forecast, around
  82: _fetch, loads, decode, raw_decode
  ...
```

By default it doesn't report duplicates of exceptions already reported, and instead presents a summary of duplicated exception error messages and stacktraces at the end.

### ``describe_python_stacktrace.py``

``describe_python_stacktrace.py`` reads a single Python exception stacktrace from stdin and writes a text format to stdout.  
