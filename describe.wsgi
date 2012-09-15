import cgi

import debugger
import httpd
import process_model

def application(environ, start_response):
    status = '200 OK'
    output = 'Hello World!xxx'

    post = cgi.FieldStorage(fp=environ['wsgi.input'],
                            environ=environ,
                            keep_blank_values=True)

    if not 'upfile' in post:
        ### error
        output = "bad"
        response_headers = [('Content-type', 'text/plain'),
                            ('Content-Length', str(len(output)))]
        start_response(status, response_headers)
        return [output]

    debugger_output = post['upfile'].value.split('\n')

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
