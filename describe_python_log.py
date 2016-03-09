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

from __future__ import print_function

import argparse
import io
import sys

import pytz

from stacktraces.python.shortcuts import process_log_file


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
    parser.add_argument('--tz', action='store', default=None,
                        help='Time zone name (e.g., "US/Eastern")')
    args = parser.parse_args()

    if args.format != 'text' and args.format != 'json':
        print('Wrong value for --format', file=sys.stderr)
        sys.exit(1)

    if args.tz:
        pytz_timezone = pytz.timezone(args.tz)
    else:
        pytz_timezone = None

    message_counts, stacktrace_counts = process_log_file(
        io.open(args.log_file_name, encoding='utf8'),
        sys.stdout,
        output_format=args.format,
        include_duplicates=args.include_duplicates,
        include_raw=args.include_raw,
        pytz_timezone=pytz_timezone,
    )

    if args.format == 'text' and not args.include_duplicates:
        print('Duplicated error messages:')
        for k in message_counts.keys():
            if message_counts[k] > 1:
                print('  %d: %s' % (message_counts[k], k))
        print('Duplicated stacktraces:')
        for k in stacktrace_counts.keys():
            if stacktrace_counts[k] > 1:
                print('  %d: %s' % (stacktrace_counts[k], k))

if __name__ == '__main__':
    main()
