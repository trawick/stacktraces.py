#!/usr/bin/python

import os
import re
import sys

import debugger
import httpd
import process_model

pid = None
corefile = None
exefile = None
debuglog = None

infolvl = 0

curarg = 1
while curarg < len(sys.argv):

    if sys.argv[curarg][:10] == '--infolvl=':
        infolvl = int(sys.argv[curarg][10:])
        curarg += 1
        continue

    if sys.argv[curarg][:11] == '--debuglog=':
        debuglog = sys.argv[curarg][11:]
        break

    try:
        pid = int(sys.argv[curarg])
    except:
        if os.access(sys.argv[curarg], os.X_OK):
            exefile = sys.argv[curarg]
        else:
            corefile = sys.argv[curarg]
    curarg += 1

if debuglog:
    debuglog = open(debuglog).readlines()
    
else:
    print "Process id:", pid
    print "Exe:       ", exefile
    print "Core file: ", corefile

p = process_model.process()

x = debugger.debugger(proc = p, pid = pid, exe = exefile, corefile = corefile, debuglog = debuglog)
x.parse()

httpd.cleanup(p)
httpd.annotate(p)
p.group()
print p.describe(infolvl)
