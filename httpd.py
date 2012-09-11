
# 't': thread name
# 's': thread state
#
# 'cdb': called directly by
# 'cb': called by

annotations = [
('t', ['cdb', 'listener_thread', 'dummy_worker'], 'MPM child listener thread'),
('t', ['cdb', 'worker_thread', 'dummy_worker'], 'MPM child worker thread'),
('t', ['cdb', 'ap_event_pod_check', 'child_main'], 'MPM child main thread'),
('t', ['cdb', 'ap_mpm_pod_check', 'child_main'], 'MPM child main thread'),
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
        for a in annotations:
            if a[0] == 't':
                # set thread name
                cond = a[1]
                tname = a[2]
                if check_condition(cond, t) != None:
                    t.set_name(tname)
            elif a[0] == 's':
                cond = a[1]
                sname = a[2]
                if check_condition(cond, t) != None:
                    t.set_state(sname)
            else:
                raise Exception('Unexpected annotation type >%s<' % a[0])

    
