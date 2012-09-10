import re
import subprocess
import sys

import httpd
import process_model

class gdb:

    def __init__(self, **kwargs):
        self.pid = kwargs.get('pid')
        self.corefile = kwargs.get('corefile')
        self.exe = kwargs.get('exe')
        self.gdbout = kwargs.get('gdbout')
        self.proc = kwargs.get('proc')
        if not self.proc:
            self.proc = process_model.process()

    def parse(self):
        if not self.gdbout:
            self.get_output()
        thr = None
        for l in self.gdbout:
            if l[:7] == 'Thread ':
                m = re.search('Thread (\d+) ', l)
                gdbtid = m.group(1)
                thr = process_model.thread(gdbtid)
                self.proc.add_thread(thr)
            elif l[:1] == '#':
                assert thr
                m = re.search('\#(\d+) +((0x[\da-f]+) in )?([^ ]+) (\([^)]*\))', l)
                if not m:
                    print >> sys.stderr, 'could not parse >%s<' % l
                    sys.exit(1)
                frameno = m.group(1)
                addr = m.group(2)
                fn = m.group(4)
                fnargs = m.group(5)
                fr = process_model.frame(frameno, fn)
                thr.add_frame(fr)

    def get_output(self):
        scr = '/tmp/cmds'
        scrfile = open(scr, "w")
        print >> scrfile, 'info sharedlibrary'
        print >> scrfile, 'info threads'
        print >> scrfile, 'thread apply all bt full'
        print >> scrfile, 'detach'
        print >> scrfile, 'quit'
        scrfile.close()

        out = '/tmp/gdbout'
        pid_or_core = self.pid
        if not pid_or_core:
            pid_or_core = self.corefile
        cmdline = ['/usr/bin/gdb',
                   '-n',
                   '-batch',
                   '-x',
                   scr,
                   self.exe,
                   pid_or_core]

        outfile = open(out, "w")
        try:
            rc = subprocess.call(cmdline, stdout=outfile, stderr=subprocess.STDOUT)
        except:
            raise Exception("couldn't run, error", sys.exc_info()[0])
        outfile.close()

        self.gdbout = open(out).readlines()

p = process_model.process()

# g = gdb(proc = p, pid = sys.argv[1], exe = '/home/trawick/inst/24-64/bin/httpd')
g = gdb(gdbout = open(sys.argv[1]).readlines(), proc = p)
g.parse()

httpd.cleanup(p)
httpd.annotate(p)
print p
