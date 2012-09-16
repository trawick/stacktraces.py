import cgi
import json

from webob import Request

import debugger
import httpd
import process_model

def application(environ, start_response):
    status = '200 OK'
    output = 'Hello World!xxx'

    req = Request(environ)

    debugger_output = req.body.split('\n')

    response_headers = [('Content-type', 'application/json')]
    start_response(status, response_headers)

    p = process_model.process(None)
    dbg = debugger.debugger(debuglog=debugger_output, proc=p)
    dbg.parse()
    httpd.cleanup(p)
    httpd.annotate(p)
    p.group()

    output = json.dumps({"success": True, 'procinfo':p.description()})

    return [output]
