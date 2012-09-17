import cgi
import json
import string
import sys
import traceback

from webob import Request

import debugger
import httpd
import process_model

def application(environ, start_response):

    req = Request(environ)

    converting = False
    try:
        debugger_output = req.body.split('\n')

        # Some gdb output from Mac OS X includes non-printable characters which cause json.dumps to die.
        for i in range(len(debugger_output)):
            try:
                json.dumps({'line': debugger_output[i]})
            except:
                # Fix it
                for cindex in range(len(debugger_output[i])):
                    if not debugger_output[i][cindex] in string.printable:
                        debugger_output[i] = debugger_output[i][:cindex] + '.' + debugger_output[i][cindex + 1:]
            
    	p = process_model.process(None)
	dbg = debugger.debugger(debuglog=debugger_output, proc=p)
        dbg.parse()
        httpd.cleanup(p)
        httpd.annotate(p)
        p.group()
        procinfo = p.description()
        converting = True
        output = json.dumps({"success": True, 'procinfo':p.description()})
        converting = False
    except:
	for info in sys.exc_info():
            print >> sys.stderr, "DESCRIBE ERROR: %s" % str(info)
	traceback.print_tb(sys.exc_info()[2])
        if converting:
            errmsg = 'An error occurred converting the output to JSON.  The file uploaded may contain unexpected characters.'
            linenum = 0
            for l in debugger_output:
                linenum += 1
                try:
                    json.dumps({'line': l})
                except:
                    errmsg += '<br />The problem may be with line %d.' % linenum
                    break
        else:
            errmsg = 'An error occurred processing the data.'
        output = json.dumps({"success": True, 'errmsg': errmsg})

    status = '200 OK'
    response_headers = [('Content-type', 'application/json')]
    start_response(status, response_headers)

    return [output]
