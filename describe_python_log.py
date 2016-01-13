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

from __future__ import print_function

import io
import sys

from stacktraces.python.shortcuts import read_log


def print_process(process):
    print(process)


def main():
    if len(sys.argv) != 2:
        print('Usage: %s <log file name>' % sys.argv[0], file=sys.stderr)
        sys.exit(1)

    read_log(tracelvl=1, logfile=io.open(sys.argv[1], encoding='utf8'), handler=print_process)

if __name__ == '__main__':
    main()
