import re

import stacktraces.process_model

RE_FILE_LINE = re.compile(r'^ *File "[^"]*", line [0-9]+, in (.*)$')


class PythonTraceback(object):

    def __init__(self, **kwargs):
        self.lines = self._combine_exception_lines(kwargs.get('lines'))
        self.proc = kwargs.get('proc')
        if not self.proc:
            self.proc = stacktraces.process_model.Process()
        self.error_msg = kwargs.get('error_msg')
        self.timestamp = kwargs.get('timestamp')
        self.thr = stacktraces.process_model.Thread(0)
        if kwargs.get('name'):
            self.thr.set_name(kwargs.get('name'))
        if self.timestamp or self.error_msg:
            self.thr.set_error_data(timestamp=self.timestamp, error_msg=self.error_msg)
        self.proc.add_thread(self.thr)

    @staticmethod
    def _combine_exception_lines(orig_lines):
        lines = list(orig_lines)
        i = len(lines) - 2  # start at next to last line
        while i > 0 and lines[i][0] != ' ' and lines[i + 1][0] != ' ':
            lines[i] = lines[i].rstrip() + '|' + lines.pop()
            i -= 1
        return lines

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
                fr = stacktraces.process_model.Frame(frameno, m.group(1))
                self.thr.add_frame(fr)
            else:
                last = l
        if last:
            self.thr.set_failure(last)
