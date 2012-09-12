#!/usr/bin/python

import os
import sys

from optparse import OptionParser

import debugger
import httpd
import process_model

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

p = process_model.process(options.pid)

x = debugger.debugger(proc = p, exe = options.exe, corefile = options.corefile, debuglog = debuglog)
x.parse()

httpd.cleanup(p)
httpd.annotate(p)
p.group()
print p.describe(options.infolvl)
