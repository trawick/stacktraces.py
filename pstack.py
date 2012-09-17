# Copyright 2012 Jeff Trawick, http://emptyhammock.com/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

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
        self.hdr = None
        self.pstackout = kwargs.get('debuglog')
        self.proc = kwargs.get('proc')
        if not self.proc:
            self.proc = process_model.process()
        self.pid = self.proc.get_pid()

    def parse(self):
        if not self.pstackout:
            self.get_output()
        thr = None
        if collect.is_hdr(self.pstackout[0]):
            self.hdr = self.pstackout[0]
            self.pstackout = self.pstackout[1:]
        if 'REM /usr/bin/pstack' in self.pstackout[0]:
            self.pstackout = self.pstackout[1:]
        m = re.search('^(\d+):[ \t]+(/[^ ]+)', self.pstackout[0])
        if m:
            self.pid = m.group(1)
            self.exe = m.group(2)
        else:
            m = re.search('^core +.* of (\d+):[ \t]+([^ ]+)', self.pstackout[0])
            if not m:
                raise Exception('could not parse >%s<' % self.pstackout[0])
            self.pid = m.group(1)
            self.exe = m.group(2)
        for l in self.pstackout[1:]:
            if 'REM ' in l and l[0:3] == 'REM ':
                break
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
        if self.pid and not self.proc.pid:
            self.proc.pid = self.pid
        if self.exe and not self.proc.exe:
            self.proc.exe = self.exe

    def get_output(self):
        self.pstackout = collect.pstack_collect(None, self.pid, self.corefile)

if __name__ == "__main__":
    print >> sys.stderr, "Don't run this directly."
