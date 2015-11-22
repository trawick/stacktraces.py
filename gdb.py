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
import sys

import collect
import process_model


class gdb:

    def __init__(self, **kwargs):
        self.corefile = kwargs.get('corefile')
        self.exe = kwargs.get('exe')
        self.hdr = None
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
        if collect.is_hdr(self.gdbout[0]):
            self.hdr = self.gdbout[0]
            self.gdbout = self.gdbout[1:]
            if not self.pid:
                self.pid = collect.get_pid(self.hdr)
            if not self.exe:
                self.exe = collect.get_exe(self.hdr)

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
            if l[0] == '#' and (l[-1:] == ',' or l[-2:] == ', ' or l[-17:] == 'is not available.' or l[-2:] == ' ('):
                if l[-2:] == ' (':
                    pending = l
                else:
                    pending = l[:-1]
                continue
            if 'Attaching to program:' in l:
                m = re.search('Attaching to program: .([^\']+)\', process (\d+)', l)
                if m:
                    if not self.exe:
                        self.exe = m.group(1)
                    if not self.pid:
                        self.pid = m.group(2)
                    continue
            if l[:7] == 'Thread ':
                m = re.search('Thread (\d+) ', l)
                gdbtid = m.group(1)
                thr = self.proc.find_thread(gdbtid)
                if not thr:
                    thr = process_model.thread(gdbtid)
                    self.proc.add_thread(thr)
                fr = None
            elif thr and l[:1] == '#':
                m = re.search('signal handler called', l)
                if m:
                    # XXX Mark thread as crashed.
                    continue
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
                # try again; make sure to handle
                #   #5  0xdeadbeef in Foo::Parse(SynTree&, int&) () from /path/to/lib
                m = re.search('\#(\d+) +((0x[\da-f]+) in )?(.*)$', l)
                if m:
                    frameno = m.group(1)
                    addr = m.group(3)
                    rest = m.group(4)
                    # filter out frames with address 0 (seen on both Linux and FreeBSD)
                    if addr and int(addr, 16) == 0:
                        continue
                    m = re.match('(.*) (\([^)]*\)) (from .*)?', rest)
                    if m:
                        fn = m.group(1)
                        fnargs = m.group(2)
                        fr = process_model.frame(frameno, fn, fnargs)
                        thr.add_frame(fr)
                        continue
                print >> sys.stderr, 'could not parse >%s<' % l
                sys.exit(1)
            elif fr:
                m = re.search('^[ \t]+([^ ]+) = (.*)$', l)
                if m:
                    fr.add_var(m.group(1), m.group(2));
        if self.pid and not self.proc.pid:
            self.proc.pid = self.pid
        if self.exe and not self.proc.exe:
            self.proc.exe = self.exe

    def get_output(self):
        self.gdbout = collect.gdb_collect(None, self.pid, self.corefile, self.exe)

if __name__ == "__main__":
    print >> sys.stderr, "Don't run this directly."
