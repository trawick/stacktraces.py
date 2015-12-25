import re

import process_model

RE_FILE_LINE = re.compile(r'^ *File "[^"]*", line [0-9]+, in (.*)$')


class PythonTraceback(object):

    def __init__(self, **kwargs):
        self.lines = kwargs.get('lines')
        self.proc = kwargs.get('proc')
        if not self.proc:
            self.proc = process_model.Process()
        self.error_msg = kwargs.get('error_msg')
        self.timestamp = kwargs.get('timestamp')
        self.thr = process_model.Thread(0)
        if kwargs.get('name'):
            self.thr.set_name(kwargs.get('name'))
        if self.timestamp or self.error_msg:
            self.thr.set_error_data(timestamp=self.timestamp, error_msg=self.error_msg)
        self.proc.add_thread(self.thr)

    def parse(self):
        frameno = 0
        last = None
        for l in self.lines:
            if l.startswith('Traceback '):
                continue
            l = l.rstrip('\r\n')
            m = RE_FILE_LINE.match(l)
            if m:
                frameno += 1
                fr = process_model.Frame(frameno, m.group(1))
                self.thr.add_frame(fr)
            else:
                last = l
        if last:
            self.thr.set_failure(last)
