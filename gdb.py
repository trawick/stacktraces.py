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
        self.gdbout = kwargs.get('debuglog')
        self.proc = kwargs.get('proc')
        if not self.proc:
            self.proc = process_model.process()

    def parse(self):
        if not self.gdbout:
            self.get_output()
        thr = None
        fr = None
        for l in self.gdbout:
            if l[:7] == 'Thread ':
                m = re.search('Thread (\d+) ', l)
                gdbtid = m.group(1)
                thr = process_model.thread(gdbtid)
                self.proc.add_thread(thr)
                fr = None
            elif thr and l[:1] == '#':
                m = re.search('\#(\d+) +((0x[\da-f]+) in )?([^ ]+) (\([^)]*\))', l)
                if not m:
                    print >> sys.stderr, 'could not parse >%s<' % l
                    sys.exit(1)
                frameno = m.group(1)
                addr = m.group(3)
                fn = m.group(4)
                fnargs = m.group(5)
                # filter out frames with address 0 (seen on both Linux and FreeBSD)
                if addr and int(addr, 16) == 0:
                    continue
                fr = process_model.frame(frameno, fn, fnargs)
                thr.add_frame(fr)
            elif fr:
                m = re.search('^[ \t]+([^ ]+) = (.*)$', l)
                if m:
                    fr.add_var(m.group(1), m.group(2));

    def get_output(self):
        scr = '/tmp/cmds'
        scrfile = open(scr, "w")
        print >> scrfile, 'info sharedlibrary'
        print >> scrfile, 'info threads'
        print >> scrfile, 'thread apply all bt full'
        if not self.corefile:
            print >> scrfile, 'detach'
        print >> scrfile, 'quit'
        scrfile.close()

        out = '/tmp/gdbout'
        if self.pid:
            pid_or_core = str(self.pid)
        else:
            pid_or_core = self.corefile
        if not pid_or_core:
            raise Exception('Either a process id or core file must be provided')

        if not self.exe:
            raise Exception('An executable file must be provided')

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
