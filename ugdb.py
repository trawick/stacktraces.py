import gdb
import httpd
import process_model
import sys

p = process_model.process()

# g = gdb(proc = p, pid = sys.argv[1], exe = '/home/trawick/inst/24-64/bin/httpd')
g = gdb.gdb(gdbout = open(sys.argv[1]).readlines(), proc = p)
g.parse()

httpd.cleanup(p)
httpd.annotate(p)
p.group()
print p

