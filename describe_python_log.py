#!/usr/bin/env python

# Copyright 2015, 2016 Jeff Trawick, http://emptyhammock.com/
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

from __future__ import print_function

from collections import defaultdict

import argparse
import io
import json
import sys

from stacktraces.python.shortcuts import read_log


def print_process(args, messages, stacktraces, need_delim, process, traceback_lines):
    thread = process.threads[0]
    st = ', '.join([f.fn for f in thread.frames])

    if not args.include_duplicates:
        if thread.failure_text:
            messages[thread.failure_text] += 1
        if thread.error_msg:
            messages[thread.error_msg] += 1
        stacktraces[st] += 1
        if stacktraces[st] > 1:
            return need_delim

    if args.format == 'text':
        if thread.error_msg:
            print(thread.error_msg)
        if thread.failure_text:
            print(thread.failure_text)
        print(st)
        if args.include_raw:
            print(''.join(traceback_lines))
        print()
    else:
        if need_delim:
            print(',')
        if args.include_raw:
            to_serialize = {
                'wrapped': process.description(wrapped=True),
                'raw': ''.join(traceback_lines)
            }
        else:
            to_serialize = process.description(wrapped=True)
        print(json.dumps(to_serialize))
        need_delim = True

    return need_delim


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('log_file_name',
                        help='name of log file to parse')
    parser.add_argument('--format', action='store', default='text',
                        help='output format ("json" or "text")')
    parser.add_argument('--include-duplicates', action='store_true',
                        help='whether to include duplicate stacktraces in output')
    parser.add_argument('--include-raw', action='store_true',
                        help='whether to include raw stacktraces in output')
    args = parser.parse_args()

    if args.format != 'text' and args.format != 'json':
        print('Wrong value for --format', file=sys.stderr)
        sys.exit(1)

    need_delim = False

    if args.format == 'json':
        print('[')

    messages = defaultdict(int)
    stacktraces = defaultdict(int)

    for p, traceback_lines in read_log(
        tracelvl=1, logfile=io.open(args.log_file_name, encoding='utf8')
    ):
        need_delim = print_process(args, messages, stacktraces, need_delim, p, traceback_lines)
    if args.format == 'json':
        print(']')

    if args.format == 'text' and not args.include_duplicates:
        print('Duplicated error messages:')
        for k in messages.keys():
            if messages[k] > 1:
                print('  %d: %s' % (messages[k], k))
        print('Duplicated stacktraces:')
        for k in stacktraces.keys():
            if stacktraces[k] > 1:
                print('  %d: %s' % (stacktraces[k], k))

if __name__ == '__main__':
    main()
