
# 't': thread name
# 's': thread state
#
# 'cdb': called directly by
# 'cb': called by

annotations = [
('t', ['cdb', 'listener_thread', 'dummy_worker'], 'MPM child listener thread'),
('t', ['cdb', 'worker_thread', 'dummy_worker'], 'MPM child worker thread'),
('t', ['cib', 'child_main', 'event_run'], 'Event MPM child main thread'),
# less specific
('t', ['is', 'child_main'], 'MPM child main thread'),
('t', ['cib', 'ap_wait_or_timeout', 'event_run'], 'Event MPM parent'),
# less specific
('t', ['is', 'ap_wait_or_timeout'], 'MPM parent'),
('s', ['cdb', 'ap_queue_pop_something', 'worker_thread'], 'waiting for connection to handle'),
('s', ['cdb', 'ap_queue_pop', 'worker_thread'], 'waiting for connection to handle'),
('s', ['cdb', 'apr_pollset_poll', 'listener_thread'], 'waiting for connection to accept'),
('s', ['is', 'ap_event_pod_check'], 'waiting for termination event'),
('s', ['is', 'ap_mpm_pod_check'], 'waiting for termination event'),
('s', ['cdb', 'apr_proc_mutex_lock', 'listener_thread'], 'waiting for accept mutex')
]

# 'db': delete frames before
# 'da': delete frames after

cleanups = [
('db', ['cdb', 'apr_thread_cond_wait', 'ap_queue_pop']),
('db', ['is', 'apr_sleep']),
('da', ['is', 'dummy_worker']),
('db', ['is', 'apr_proc_mutex_lock']),
('db', ['is', 'ap_mpm_pod_check']),
('db', ['is', 'ap_event_pod_check']),
('db', ['is', 'apr_pollset_poll']),
('db', ['is', 'apr_thread_cond_wait']),
('da', ['is', 'main']),
]

def check_condition(cond, t):
    """ Check specified condition, return range of frames which match the condition (or None) """
    for i in range(len(t.frames)):
        if t.frames[i].fn == cond[1]:
            if cond[0] == 'is':
                return (i, i)
            if cond[0] == 'cdb':
                if i + 1 < len(t.frames) and t.frames[i + 1].fn == cond[2]:
                    return (i, i + 1)
            elif cond[0] == 'cib':
                j = i + 1
                while j < len(t.frames):
                    print 'comparing %s and %s' % (t.frames[j].fn, cond[2])
                    if t.frames[j].fn == cond[2]:
                        print 'found'
                        return (i, j)
                    j += 1
            else:
                raise Exception('Unexpected condition type >%s<' % cond[0])
    return None

def cleanup(p):
    for t in p.threads:
        for c in cleanups:
            i = check_condition(c[1], t)
            if i != None:
                if c[0] == 'db':
                    t.frames = t.frames[i[0]:]
                elif c[0] == 'da':
                    t.frames = t.frames[:i[1] + 1]
                else:
                    raise Exception('Unexpected cleanup type >%s<' % c[0])
    
def annotate(p):
    for t in p.threads:
        found = {} # don't test less-specific annotations of this type
        for a in annotations:
            if a[0] == 't':
                if not 't' in found:
                    # set thread name
                    cond = a[1]
                    tname = a[2]
                    if check_condition(cond, t) != None:
                        found['t'] = True
                        t.set_name(tname)
            elif a[0] == 's':
                if not 's' in found:
                    cond = a[1]
                    sname = a[2]
                    if check_condition(cond, t) != None:
                        found['s'] = True
                        t.set_state(sname)
            else:
                raise Exception('Unexpected annotation type >%s<' % a[0])

    
