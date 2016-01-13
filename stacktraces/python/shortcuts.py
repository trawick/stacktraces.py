import re

from six import text_type

from stacktraces import process_model, thread_analyzer
from stacktraces.python import stacktrace


def describe_lines(traceback_lines):
    p = process_model.Process(0)
    ptb = stacktrace.PythonTraceback(
        proc=p, lines=traceback_lines, name='Python Exception'
    )
    ptb.parse()
    # thread_analyzer.cleanup(p, my_cleanups)
    # thread_analyzer.annotate(p, my_annotations)
    p.group()  # only one thread, but this allows str(p) to work
    return text_type(p)


TRACE_MSG_RE_1 = re.compile(r'^\[([^]]+)\] ERROR \[[^]]+\] (.*)\n?$')
TRACE_MSG_RE_2 = re.compile(r'^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d).*(INFO|WARNING|ERROR) +(.*)\n?$')


def parse_trace_msg(msg):
    m = TRACE_MSG_RE_1.match(msg)
    if m:
        timestamp, error_msg = m.groups()
    else:
        m = TRACE_MSG_RE_2.match(msg)
        if m:
            timestamp, _, error_msg = m.groups()
        else:
            timestamp, error_msg = None, None
    return timestamp, error_msg


def handle_traceback(traceback_lines, msg, tracelvl, handler, cleanups, annotations):
    # We just have a traceback from an individual thread, so skip:
    # . ProcessGroup representation
    # . Process.group(), which finds threads in a process with same backtrace

    timestamp, error_msg = parse_trace_msg(msg)
    # if not timestamp:
    #     raise ValueError('Cannot parse log message "%s"' % msg)

    # Ignore error message in the related log message for now; it seems to be
    # always duplicated within the traceback output
    p = process_model.Process(0)
    ptb = stacktrace.PythonTraceback(
        proc=p, lines=traceback_lines, timestamp=timestamp, name='WhatNameHere?'
    )
    ptb.parse()
    thread_analyzer.cleanup(p, cleanups)
    thread_analyzer.annotate(p, annotations)
    p.group()  # only one thread, but this allows str(p) to work
    if tracelvl > 1:
        print('-------------')
        print(traceback_lines)
    handler(process=p)


class Line(object):
    def __init__(self, line):
        self.line = line
        self.is_traceback = line.startswith('Traceback ')
        self.is_log_msg = False
        if not self.is_traceback:
            timestamp, _ = parse_trace_msg(line)
            if timestamp:
                self.is_log_msg = True


class ParseState(object):
    def __init__(self):
        self.in_traceback = False
        self.traceback_lines = []
        self.traceback_log_msg = None


def read_log(tracelvl, logfile, handler, cleanups=(), annotations=()):
    prev = None
    s = ParseState()

    while True:
        l = logfile.readline()
        if l == '':
            break
        l = Line(l)
        if l.is_traceback:
            if s.in_traceback:
                handle_traceback(s.traceback_lines, s.traceback_log_msg, tracelvl, handler, cleanups, annotations)
                s = ParseState()
            s.in_traceback = True
            s.traceback_log_msg = prev.line
        elif l.is_log_msg and s.traceback_lines:
            handle_traceback(s.traceback_lines, s.traceback_log_msg, tracelvl, handler, cleanups, annotations)
            s = ParseState()
        if s.in_traceback:
            s.traceback_lines.append(l.line)
        prev = l
    if s.in_traceback:
        handle_traceback(s.traceback_lines, s.traceback_log_msg, tracelvl, handler, cleanups, annotations)
        # s = ParseState()
