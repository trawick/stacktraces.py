#!/usr/bin/env python

# Copyright 2015 Jeff Trawick, http://emptyhammock.com/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# WHAT SHOULD BE DONE?
# 1. for nested exceptions, save multiple exceptions with some clear relationship

import io
import re
import sys

from stacktraces import process_model, thread_analyzer
from stacktraces.python import stacktrace

# XXX pass module on command-line?  or YAML file?
my_django_cleanups = (
)

my_annotations = (
)

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


def handle_traceback(traceback_lines, msg, tracelvl):
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
    thread_analyzer.cleanup(p, my_django_cleanups)
    thread_analyzer.annotate(p, my_annotations)
    p.group()  # only one thread, but this allows str(p) to work
    if tracelvl > 1:
        print '-------------'
        print traceback_lines
    print p


class Line(object):
    def __init__(self, line):
        self.line = line
        self.is_traceback = line.startswith('Traceback ')
        self.is_log_msg = False
        if not self.is_traceback:
            timestamp, _ = parse_trace_msg(line)
            if timestamp:
                self.is_log_msg = True


def parse_line(l):
    """On input get a line (string) from the file, on output return Line object
    representing that line."""
    return Line(l)


class ParseState(object):
    def __init__(self):
        self.in_traceback = False
        self.traceback_lines = []
        self.traceback_log_msg = None


def read_log(tracelvl, logfile_name):
    prev = None
    s = ParseState()

    logfile = io.open(logfile_name, encoding='utf8')
    while True:
        l = logfile.readline()
        if l == '':
            break
        l = parse_line(l)
        if l.is_traceback:
            if s.in_traceback:
                handle_traceback(s.traceback_lines, s.traceback_log_msg, tracelvl)
                s = ParseState()
            s.in_traceback = True
            s.traceback_log_msg = prev.line
        elif l.is_log_msg and s.traceback_lines:
            handle_traceback(s.traceback_lines, s.traceback_log_msg, tracelvl)
            s = ParseState()
        if s.in_traceback:
            s.traceback_lines.append(l.line)
        prev = l
    if s.in_traceback:
        handle_traceback(s.traceback_lines, s.traceback_log_msg, tracelvl)
        # s = ParseState()


def main():
    if len(sys.argv) != 2:
        print >> sys.stderr, 'Usage: %s <log file name>' % sys.argv[0]
        sys.exit(1)

    read_log(tracelvl=1, logfile_name=sys.argv[1])

if __name__ == '__main__':
    main()
