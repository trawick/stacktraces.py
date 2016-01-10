def check_condition(cond, t):
    """ Check specified condition, return range of frames which match the condition (or None) """
    for i in range(len(t.frames)):
        if t.frames[i].fn == cond[1] or (cond[0] == 'ismatch' and cond[1] in t.frames[i].fn):
            if cond[0] == 'is' or cond[0] == 'ismatch':
                return i, i
            if cond[0] == 'cdb':
                if i + 1 < len(t.frames) and t.frames[i + 1].fn == cond[2]:
                    return i, i + 1
            elif cond[0] == 'cib':
                j = i + 1
                while j < len(t.frames):
                    if t.frames[j].fn == cond[2]:
                        return i, j
                    j += 1
            else:
                raise Exception('Unexpected condition type >%s<' % cond[0])
    return None


def cleanup(p, cleanups):
    for t in p.threads:
        for c in cleanups:
            i = check_condition(c[1], t)
            if i is not None:
                if c[0] == 'db':
                    t.frames = t.frames[i[0]:]
                elif c[0] == 'da':
                    t.frames = t.frames[:i[1] + 1]
                elif c[0] == 'dda':
                    t.frames = t.frames[:i[1]]
                elif c[0] == 'd':
                    t.frames = t.frames[:i[0]] + t.frames[i[1] + 1:]
                elif c[0] == 'df':
                    t.frames = t.frames[:i[0]] + t.frames[i[0] + 1:]
                else:
                    raise Exception('Unexpected cleanup type >%s<' % c[0])


def annotate(p, annotations):
    for t in p.threads:
        found = {}  # don't test less-specific annotations of this type
        for a in annotations:
            if a[0] == 't':
                if 't' not in found:
                    # set thread name
                    cond = a[1]
                    tname = a[2]
                    if check_condition(cond, t) is not None:
                        found['t'] = True
                        t.set_name(tname)
            elif a[0] == 's':
                if 's' not in found:
                    cond = a[1]
                    sname = a[2]
                    if check_condition(cond, t) is not None:
                        found['s'] = True
                        t.set_state(sname)
            else:
                raise Exception('Unexpected annotation type >%s<' % a[0])
