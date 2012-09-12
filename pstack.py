import re
import subprocess
import sys

import httpd
import process_model

class pstack:

    def __init__(self, **kwargs):
        self.pid = kwargs.get('pid')
        self.corefile = kwargs.get('corefile')
        self.exe = kwargs.get('exe')
        self.pstackout = kwargs.get('debuglog')
        self.proc = kwargs.get('proc')
        if not self.proc:
            self.proc = process_model.process()

    def parse(self):
        if not self.pstackout:
            self.get_output()
        thr = None
        m = re.search('^(\d+):[ \t]+(/[^ ]+)', self.pstackout[0])
        if not m:
            raise Exception('could not parse %s' % self.pstackout[0])
        self.pid = m.group(1)
        self.exe = m.group(2)
        for l in self.pstackout[1:]:
            m = re.search('^-+ +lwp# +\d+ +/ +thread# +(\d+) +', l)
            if m:
                thr = process_model.thread(m.group(1))
                self.proc.add_thread(thr)
                frameno = 0
                continue
            m = re.search('^ +([\da-f]+) +([^ ]+) +(\([^)]*\))', l)
            if m:
                addr = m.group(1)
                fn = m.group(2)
                fnargs = m.group(3)
                frameno += 1
                fr = process_model.frame(frameno, fn)
                thr.add_frame(fr)
                continue
            m = re.search('^ +([\da-f]+) +([^ ]+) *(\([^)]*\)), exit value =', l)
            if m:
                thr.set_exited()

    def get_output(self):
        out = '/tmp/pstackout'
        pid_or_core = self.pid
        if not pid_or_core:
            pid_or_core = self.corefile
        cmdline = ['/usr/bin/pstack',
                   pid_or_core]
        outfile = open(out, "w")
        try:
            rc = subprocess.call(cmdline, stdout=outfile, stderr=subprocess.STDOUT)
        except:
            raise Exception("couldn't run, error", sys.exc_info()[0])
        outfile.close()

        self.pstackout = open(out).readlines()
