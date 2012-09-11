#!/usr/bin/python

import os
import sys

import gdb
import httpd
import process_model
import pstack

pid = None
corefile = None
exefile = None

curarg = 1
while curarg < len(sys.argv):
    try:
        pid = int(sys.argv[curarg])
    except:
        if os.access(sys.argv[curarg], os.X_OK):
            exefile = sys.argv[curarg]
        else:
            corefile = sys.argv[curarg]
    curarg += 1

print "Process id:", pid
print "Exe:       ", exefile
print "Core file: ", corefile

p = process_model.process()

if os.access('/usr/bin/pstack', os.X_OK):
    pass
else:
    g = gdb.gdb(proc = p, pid = pid, exe = exefile, corefile = corefile)
    g.parse()

httpd.cleanup(p)
httpd.annotate(p)
p.group()
print p
