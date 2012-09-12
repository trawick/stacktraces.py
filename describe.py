#!/usr/bin/python

import os
import re
import sys

import gdb
import httpd
import process_model
import pstack

pid = None
corefile = None
exefile = None
debuglog = None

use_pstack = False
use_gdb = False

curarg = 1
while curarg < len(sys.argv):
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
    if re.search('^(\d+):[ \t]+', debuglog[0]) and re.search('------- +lwp', debuglog[1]):
        use_pstack = True
    else:
        use_gdb = True
    
else:
    print "Process id:", pid
    print "Exe:       ", exefile
    print "Core file: ", corefile
    if os.access('/usr/bin/pstack', os.X_OK):
        use_pstack = True
    else:
        use_gdb = True

p = process_model.process()

if use_pstack:
    x = pstack.pstack(proc = p, pid = pid, exe = exefile, corefile = corefile, debuglog = debuglog)
    x.parse()
else:
    x = gdb.gdb(proc = p, pid = pid, exe = exefile, corefile = corefile, debuglog = debuglog)
    x.parse()

httpd.cleanup(p)
httpd.annotate(p)
p.group()
print p.describe(1)
