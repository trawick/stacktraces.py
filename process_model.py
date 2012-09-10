class thread:

    def __init__(self, tid):
        self.tid = tid
        self.frames = []
        self.name = None
        self.state = None

    def __str__(self):
        s = ''
        s += '[%s]' % self.tid
        s += ' '
        if self.name:
            s += self.name
            s += ' '
        if self.state:
            s += '(%s) ' % self.state
        s += '\n  '
        for f in self.frames:
            s += f.__str__()
            s += ', '
        return s

    def add_frame(self, frame):
        self.frames.append(frame)

    def set_name(self, name):
        self.name = name

    def set_state(self, state):
        self.state = state

class process:

    def __init__(self, pid = None):
        self.pid = pid
        self.threads = []

    def __str__(self):
        s = ''
        for t in self.threads:
            s += t.__str__()
            s += '\n'
        return s

    def add_thread(self, thr):
        self.threads.append(thr)

class frame:

    def __init__(self, id, fn):
        self.id = id
        self.fn = fn

        if '@@GLIBC' in fn:
            self.fn = fn[:fn.index('@@GLIBC')]

    def __str__(self):
        return self.fn
