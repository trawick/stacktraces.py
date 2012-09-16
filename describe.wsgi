import cgi
import json

from webob import Request

import debugger
import httpd
import process_model

def application(environ, start_response):

    req = Request(environ)

    try:
        debugger_output = req.body.split('\n')
    	p = process_model.process(None)
	dbg = debugger.debugger(debuglog=debugger_output, proc=p)
        dbg.parse()
        httpd.cleanup(p)
        httpd.annotate(p)
        p.group()
        procinfo = p.description()
        output = json.dumps({"success": True, 'procinfo':p.description()})
    except:
        output = json.dumps({"success": True, 'errmsg': 'An error occurred processing the data'})

    status = '200 OK'
    response_headers = [('Content-type', 'application/json')]
    start_response(status, response_headers)

    return [output]
