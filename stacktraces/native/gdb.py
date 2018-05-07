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

from __future__ import print_function

import re
import sys

from stacktraces.native import collect
import stacktraces.process_model


class Gdb:

    def __init__(self, **kwargs):
        self.corefile = kwargs.get('corefile')
        self.exe = kwargs.get('exe')
        self.hdr = None
        self.gdbout = kwargs.get('debuglog')
        self.proc = kwargs.get('proc')
        if not self.proc:
            self.proc = stacktraces.process_model.Process()
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

        for line in self.gdbout:
            if line:
                line = line.rstrip('\r\n')
            if not line:
                continue
            if '---Type <return' in line:
                continue
            if pending:
                line = pending + line
                pending = None
            if line[0] == '#' and (line[-1:] == ',' or line[-2:] == ', ' or
                                   line[-17:] == 'is not available.' or line[-2:] == ' ('):
                if line[-2:] == ' (':
                    pending = line
                else:
                    pending = line[:-1]
                continue
            if 'Attaching to program:' in line:
                m = re.search('Attaching to program: .([^\']+)\', process (\d+)', line)
                if m:
                    if not self.exe:
                        self.exe = m.group(1)
                    if not self.pid:
                        self.pid = m.group(2)
                    continue
            if line[:7] == 'Thread ':
                m = re.search('Thread (\d+) ', line)
                gdbtid = m.group(1)
                thr = self.proc.find_thread(gdbtid)
                if not thr:
                    thr = stacktraces.process_model.Thread(gdbtid)
                    self.proc.add_thread(thr)
                fr = None
            elif thr and line[:1] == '#':
                m = re.search('signal handler called', line)
                if m:
                    # XXX Mark thread as crashed.
                    continue
                m = re.search('#(\d+) +((0x[\da-f]+) in )?([^ ]+) (\([^)]*\))', line)
                if m:
                    frameno = m.group(1)
                    addr = m.group(3)
                    fn = m.group(4)
                    fnargs = m.group(5)
                    # filter out frames with address 0 (seen on both Linux and FreeBSD)
                    if addr and int(addr, 16) == 0:
                        continue
                    fr = stacktraces.process_model.Frame(frameno, fn, fnargs)
                    thr.add_frame(fr)
                    continue
                # try again; make sure to handle
                #   #5  0xdeadbeef in Foo::Parse(SynTree&, int&) () from /path/to/lib
                m = re.search('#(\d+) +((0x[\da-f]+) in )?(.*)$', line)
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
                        fr = stacktraces.process_model.Frame(frameno, fn, fnargs)
                        thr.add_frame(fr)
                        continue
                print('could not parse >%s<' % line, file=sys.stderr)
                sys.exit(1)
            elif fr:
                m = re.search('^[ \t]+([^ ]+) = (.*)$', line)
                if m:
                    fr.add_var(m.group(1), m.group(2))
        if self.pid and not self.proc.pid:
            self.proc.pid = self.pid
        if self.exe and not self.proc.exe:
            self.proc.exe = self.exe

    def get_output(self):
        self.gdbout = collect.gdb_collect(None, self.pid, self.corefile, self.exe)
