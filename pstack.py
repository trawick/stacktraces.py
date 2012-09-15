import re
import subprocess
import sys

import collect
import httpd
import process_model

class pstack:

    def __init__(self, **kwargs):
        self.corefile = kwargs.get('corefile')
        self.exe = kwargs.get('exe')
        self.pstackout = kwargs.get('debuglog')
        self.proc = kwargs.get('proc')
        if not self.proc:
            self.proc = process_model.process()
        self.pid = self.proc.get_pid()

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
        self.pstackout = collect.pstack_collect(None, self.pid, self.corefile)
