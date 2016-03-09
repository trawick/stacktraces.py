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

LVL_SHOW_PROCESSES = 0
LVL_SHOW_THREADS = 1
LVL_SHOW_FRAMES = 2
LVL_SHOW_ARGS = 3
LVL_SHOW_VARS = 4

MAJOR_VERSION_KEY = 'mv'
MAJOR_VERSION = 1


class Thread:

    def __init__(self, tid):
        self.tid = tid
        self.frames = []
        self.name = None
        self.state = None
        self.exited = False
        self.failure_text = None
        self.error_msg = None
        self.timestamp = None
        self.isotimestamp = None

    def common_str(self):
        s = ''
        s += '[%s]' % self.tid
        need_comma = False
        if self.name:
            s += ' '
            s += self.name
            need_comma = True
        if self.state:
            s += ' (%s)' % self.state
            need_comma = True
        if self.error_msg:
            if need_comma:
                s += ','
            s += ' <%s>' % self.failure_text
            need_comma = True
        if self.failure_text:
            if need_comma:
                s += ','
            s += ' Failure was <%s>' % self.failure_text
            need_comma = True
        if self.timestamp:
            if need_comma:
                s += ','
            s += ' at <%s>' % self.timestamp
        s += '\n'
        return s

    def __str__(self):
        s = self.common_str() + '  '
        for f in self.frames:
            s += f.__str__()
            s += ', '
        return s

    def describe(self, level=0):
        if level < LVL_SHOW_FRAMES:
            return self.__str__()
        s = self.common_str()
        for f in self.frames:
            s += ' ' + f.describe(level)
        return s

    def description(self, wrapped=False):
        info = dict()

        if len(self.frames):
            frames = []
            for f in self.frames:
                frames.append(f.description())
            info['frames'] = frames

        if self.tid:
            info['tid'] = self.tid
        if self.name:
            info['name'] = self.name
        if self.state:
            info['state'] = self.state
        if self.error_msg:
            info['errormsg'] = self.error_msg
        if self.failure_text:
            info['failure'] = self.failure_text
        # original timestamp for display
        if self.timestamp:
            info['timestamp'] = self.timestamp
        # parsed, formatted timestamp for processing
        if self.isotimestamp:
            info['isotimestamp'] = self.isotimestamp

        if wrapped:
            return {
                'thread': info,
                MAJOR_VERSION_KEY: MAJOR_VERSION,
            }
        else:
            return info

    def set_exited(self, flag=True):
        self.exited = flag

    def add_frame(self, frame):
        self.frames.append(frame)

    def set_name(self, name):
        self.name = name

    def set_state(self, state):
        self.state = state

    def set_failure(self, failure_text):
        self.failure_text = failure_text

    def set_error_data(self, timestamp=None, isotimestamp=None, error_msg=None):
        self.timestamp = timestamp
        self.isotimestamp = isotimestamp
        self.error_msg = error_msg

    def same_backtrace(self, thr2):
        if len(self.frames) != len(thr2.frames):
            return False
        for i in range(len(self.frames)):
            if self.frames[i].fn != thr2.frames[i].fn:
                return False
        return True


class ThreadGroup:
    """ group of threads with same characteristics, such as active frames """

    def __init__(self, thr):
        self.count = 0
        self.threads = [thr]

    def __str__(self):
        return self.threads[0].__str__()

    def add_thread(self, thr):
        self.threads.append(thr)

    def description(self, wrapped=False):
        tids = []
        for t in self.threads:
            tids.append(t.tid)
        desc = {
            'thread_ids': tids,
        }
        if wrapped:
            return {
                'threadgroup': desc,
                MAJOR_VERSION_KEY: MAJOR_VERSION,
            }
        else:
            return desc


class ProcessGroup:

    def __init__(self):
        self.processes = []

    def add_process(self, proc):
        self.processes.append(proc)

    def __str__(self):
        s = ''
        for p in self.processes:
            s += p.__str__()
            s += '\n'
        return s

    def describe(self, level=0):
        if level >= 1:
            s = ''
            for p in self.processes:
                s += p.describe(level)
                s += '\n'
            return s
        else:
            return self.__str__()

    def description(self, wrapped=False):
        procs = []
        for p in self.processes:
            procs.append(p.description())
        desc = {
            'processgroupname': 'no-name',
            'processes': procs,
        }
        if wrapped:
            return {
                'processgroup': desc,
                MAJOR_VERSION_KEY: MAJOR_VERSION,
            }
        else:
            return desc


class Process:

    def __init__(self, pid=None):
        self.pid = pid
        self.exe = None
        self.threads = []
        self.threadgroups = []

    def __str__(self):
        s = ''
        if self.pid:
            s += 'Pid %s ' % self.pid
        if self.exe:
            s += 'Executable %s ' % self.exe
        if s != '':
            s += '\n'
        if self.threads and not self.threadgroups:
            raise ValueError('Call Process.group() first to group threads')
        for tg in self.threadgroups:
            s += '%d * ' % len(tg.threads)
            s += tg.__str__()
            s += '\n'
        return s

    def describe(self, level=0):
        if level >= 1:
            s = ''
            if self.pid:
                s += 'Pid %s ' % self.pid
            if self.exe:
                s += 'Executable %s ' % self.exe
            if s != '':
                s += '\n'
            for t in self.threads:
                s += t.describe(level)
                s += '\n'
        else:
            s = self.__str__()
        return s

    def description(self, wrapped=False):
        threads = []
        for t in self.threads:
            threads.append(t.description())
        threadgroups = []
        for t in self.threadgroups:
            threadgroups.append(t.description())
        data = {
            'processname': 'no-name',
            'threads': threads,
            'threadgroups': threadgroups,
        }
        if self.pid:
            data['pid'] = self.pid
        if self.exe:
            data['exe'] = self.exe
        if wrapped:
            return {
                'process': data,
                MAJOR_VERSION_KEY: MAJOR_VERSION,
            }
        else:
            return data

    def add_thread(self, thr):
        self.threads.append(thr)

    def find_thread(self, thrid):
        for t in self.threads:
            if t.tid == thrid:
                return t
        return None

    def group(self):
        for t in self.threads:
            if t.exited:
                continue
            found = False
            for g in self.threadgroups:
                if t.same_backtrace(g.threads[0]):
                    g.add_thread(t)
                    found = True
                    break
            if not found:
                self.threadgroups.append(ThreadGroup(t))

    def get_pid(self):
        return self.pid


class Frame:

    def __init__(self, frame_id, fn, args=None):
        self.id = frame_id
        self.fn = fn
        self.args = args
        self.vars = {}

        if '@@GLIBC' in fn:
            self.fn = fn[:fn.index('@@GLIBC')]

    def __str__(self):
        return self.fn

    def describe(self, level=0):
        if level < LVL_SHOW_ARGS:
            return self.__str__()
        s = '#%s %s' % (self.id, self.fn)
        if level >= LVL_SHOW_ARGS and self.args:
            s += self.args
        s += '\n'
        if level >= LVL_SHOW_VARS and len(self.vars):
            for k in self.vars.keys():
                s += '  %s=%s\n' % (k, self.vars[k])
        return s

    def add_var(self, var, val):
        self.vars[var] = val

    def description(self, wrapped=False):
        desc = {
            'id': self.id,
            'fn': self.fn,
        }
        if self.args:
            desc['args'] = self.args
        if self.vars:
            desc['vars'] = self.vars
        if wrapped:
            return {
                'frame': desc,
                MAJOR_VERSION_KEY: MAJOR_VERSION,
            }
        else:
            return desc
