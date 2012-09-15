#!/usr/bin/env python

# Copyright 2012 Jeff Trawick, http://emptyhammock.com/
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

import os
import re
import subprocess
import sys

from optparse import OptionParser

import debugger
import httpd
import process_model

def add_children(pids):
    cmd = ['ps', '-A', '-o', 'pid,ppid']
    stdout = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
    for l in stdout.split('\n'):
        m = re.search('(\d+)[ \t]*%s' % pids[0], l)
        if m:
            pids.append(m.group(1))

parser = OptionParser()
parser.add_option("-l", "--debuglog", dest="debuglog", type="string",
                  action="store",
                  help="specify log with debugger output to analyze")
parser.add_option("-p", "--pid", dest="pid", type="int",
                  action="store",
                  help="specify process id to analyze")
parser.add_option("-f", "--follow", dest="follow",
                  action="store_true",
                  help="describe child processes too")
parser.add_option("-e", "--exe", dest="exe", type="string",
                  action="store",
                  help="point to executable for process")
parser.add_option("-c", "--corefile", dest="corefile", type="string",
                  action="store",
                  help="point to core file to examine")
parser.add_option("-i", "--infolvl", dest="infolvl", type="int",
                  action="store",
                  help="specify level of information to be displayed")

(options, args) = parser.parse_args()

mutually_exclusive = {"debuglog": "pid",
                      "debuglog": "corefile",
                      "debuglog": "follow",
                      "pid": "corefile",
                      "follow": "corefile"}

for (k,v) in mutually_exclusive.items():
    if eval('options.' + k) and eval('options.' + v):
        parser.error("--%s and --%s are mutually exclusive" % (k, v))

if options.debuglog:
    debuglog = open(options.debuglog).readlines()
else:
    debuglog = None

pids = [options.pid]

if options.follow:
    add_children(pids)

group = process_model.process_group()

for pid in pids:
    p = process_model.process(pid)
    group.add_process(p)

    x = debugger.debugger(proc = p, exe = options.exe, corefile = options.corefile, debuglog = debuglog)
    x.parse()

    httpd.cleanup(p)
    httpd.annotate(p)
    p.group()

print group.describe(options.infolvl)
