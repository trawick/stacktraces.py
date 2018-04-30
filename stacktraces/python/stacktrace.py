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
        self.isotimestamp = kwargs.get('isotimestamp')
        self.thr = stacktraces.process_model.Thread(0)
        if kwargs.get('name'):
            self.thr.set_name(kwargs.get('name'))
        if self.timestamp or self.isotimestamp or self.error_msg:
            self.thr.set_error_data(
                timestamp=self.timestamp, isotimestamp=self.isotimestamp,
                error_msg=self.error_msg
            )
        self.proc.add_thread(self.thr)

    @staticmethod
    def _combine_exception_lines(orig_lines):
        lines = list(orig_lines)
        # Remove any trailing empty line.
        if len(lines) > 0 and lines[len(lines) - 1] == '':
            lines = lines[:-1]
        i = len(lines) - 2  # start at next to last line
        while i > 0 and lines[i][0] != ' ' and lines[i + 1][0] != ' ':
            lines[i] = lines[i].rstrip() + '|' + lines.pop()
            i -= 1
        return lines

    def parse(self):
        frameno = 0
        last = None
        for line in self.lines:
            if line.startswith('Traceback '):
                continue
            line = line.rstrip('\r\n')
            m = RE_FILE_LINE.match(line)
            if m:
                frameno += 1
                fr = stacktraces.process_model.Frame(frameno, m.group(1))
                self.thr.add_frame(fr)
            else:
                if last and line and last[0] != ' ' and line[:2] == '  ':
                    last = u'%s\n%s' % (last, line)
                else:
                    last = line
        if last:
            self.thr.set_failure(last)
