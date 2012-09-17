import os
import re
import sys

import collect
import gdb
import pstack
import process_model

class debugger:

    def __init__(self, **kwargs):
        self.pid = kwargs.get('pid')
        self.corefile = kwargs.get('corefile')
        self.exe = kwargs.get('exe')
        self.debuglog = kwargs.get('debuglog')
        self.proc = kwargs.get('proc')
        if not self.proc:
            self.proc = process_model.process(self.pid)

        self.use_pstack = False
        self.use_gdb = False

        if self.debuglog:
            if collect.is_hdr(self.debuglog[0]):
                tool = collect.get_tool(self.debuglog[0])
                if tool == 'pstack':
                    self.use_pstack = True
                elif tool == 'gdb':
                    self.use_gdb = True
                else:
                    raise Exception("Unexpected tool %s" % tool)
            else:
                if re.search('^(\d+):[ \t]+', self.debuglog[0]) and re.search('------- +lwp', self.debuglog[1]):
                    self.use_pstack = True
                elif re.search('^core .* of \d+:', self.debuglog[0]):
                    self.use_pstack = True
                else:
                    self.use_gdb = True
        else:
            if 'sunos' in sys.platform:
                self.use_pstack = True
            else:
                self.use_gdb = True

        if self.use_pstack:
            self.x = pstack.pstack(proc = self.proc, exe = self.exe, corefile = self.corefile, debuglog = self.debuglog)
        else:
            self.x = gdb.gdb(proc = self.proc, exe = self.exe, corefile = self.corefile, debuglog = self.debuglog)

    def parse(self):
        self.x.parse()
