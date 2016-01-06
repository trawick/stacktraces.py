import json
import io
import sys

import debugger
import httpd
import process_model
import thread_analyzer


def main():
    p = process_model.Process(None)
    dbg = debugger.Debugger(debuglog=io.open(sys.argv[1], encoding='utf8').readlines(), proc=p)
    dbg.parse()
    thread_analyzer.cleanup(p, httpd.httpd_cleanups)
    thread_analyzer.annotate(p, httpd.httpd_annotations)
    p.group()
    io.open(sys.argv[2], 'w', encoding='utf8').write(unicode(json.dumps(p.description())))

if __name__ == '__main__':
    main()
