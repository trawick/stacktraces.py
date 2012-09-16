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

class gdb:

    def __init__(self, **kwargs):
        self.corefile = kwargs.get('corefile')
        self.exe = kwargs.get('exe')
        self.gdbout = kwargs.get('debuglog')
        self.proc = kwargs.get('proc')
        if not self.proc:
            self.proc = process_model.process()
        self.pid = self.proc.get_pid()

    def parse(self):
        if not self.gdbout:
            self.get_output()
        thr = None
        fr = None
        pending = None
        for l in self.gdbout:
            if l:
                l = l.rstrip('\r\n')
            if not l:
                continue
            if '---Type <return' in l:
                continue
            if pending:
                l = pending + l
                pending = None
            if l[0] == '#' and (l[-1:] == ',' or l[-17:] == 'is not available.'):
                pending = l[:-1]
                continue
            if l[:7] == 'Thread ':
                m = re.search('Thread (\d+) ', l)
                gdbtid = m.group(1)
                thr = process_model.thread(gdbtid)
                self.proc.add_thread(thr)
                fr = None
            elif thr and l[:1] == '#':
                m = re.search('\#(\d+) +((0x[\da-f]+) in )?([^ ]+) (\([^)]*\))', l)
                if m:
                    frameno = m.group(1)
                    addr = m.group(3)
                    fn = m.group(4)
                    fnargs = m.group(5)
                # filter out frames with address 0 (seen on both Linux and FreeBSD)
                    if addr and int(addr, 16) == 0:
                        continue
                    fr = process_model.frame(frameno, fn, fnargs)
                    thr.add_frame(fr)
                    continue
                m = re.search('signal handler called', l)
                if m:
                    # XXX Mark thread as crashed.
                    continue
                print >> sys.stderr, 'could not parse >%s<' % l
                sys.exit(1)
            elif fr:
                m = re.search('^[ \t]+([^ ]+) = (.*)$', l)
                if m:
                    fr.add_var(m.group(1), m.group(2));

    def get_output(self):
        self.gdbout = collect.gdb_collect(None, self.pid, self.corefile, self.exe)

if __name__ == "__main__":
    print >> sys.stderr, "Don't run this directly."
