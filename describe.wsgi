import cgi

from webob import Request

import debugger
import httpd
import process_model

def application(environ, start_response):
    status = '200 OK'
    output = 'Hello World!xxx'

    req = Request(environ)

    debugger_output = req.body.split('\n')

    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)

    p = process_model.process(None)
    dbg = debugger.debugger(debuglog=debugger_output, proc=p)
    dbg.parse()
    httpd.cleanup(p)
    httpd.annotate(p)
    p.group()

    output = p.describe(0)
    return [output]
