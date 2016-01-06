import unittest

from stacktraces.py_shortcuts import describe_lines

PYTHON_STACKTRACE = u"""[14/Mar/2015 01:37:05] ERROR [django.request:231] Internal Server Error: /walk/ExYu
Traceback (most recent call last):
  File "/home/trawick/git/walking/envs/walking/lib/python2.7/site-packages/django/core/handlers/base.py", line 111, in get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
  File "/home/trawick/git/walking/envs/walking/lib/python2.7/site-packages/django/contrib/auth/decorators.py", line 21, in _wrapped_view
    return view_func(request, *args, **kwargs)
  File "/home/trawick/git/walking/src/walking/walks/views.py", line 58, in index
    forecast = wo.weather_forecast()
  File "/home/trawick/git/walking/src/walking/walks/models.py", line 81, in weather_forecast
    city, raw_forecast = w.around(start, 4 * 60 * 60)
  File "/home/trawick/git/walking/src/walking/walking/weather.py", line 132, in around
    d = Weather._fetch(uri, self._validate_around_weather)
  File "/home/trawick/git/walking/src/walking/walking/weather.py", line 42, in _fetch
    c.request('GET', uri)
  File "/home/trawick/python-2.7/lib/python2.7/httplib.py", line 995, in request
    self._send_request(method, url, body, headers)
  File "/home/trawick/python-2.7/lib/python2.7/httplib.py", line 1029, in _send_request
    self.endheaders(body)
  File "/home/trawick/python-2.7/lib/python2.7/httplib.py", line 991, in endheaders
    self._send_output(message_body)
  File "/home/trawick/python-2.7/lib/python2.7/httplib.py", line 844, in _send_output
    self.send(msg)
  File "/home/trawick/python-2.7/lib/python2.7/httplib.py", line 806, in send
    self.connect()
  File "/home/trawick/python-2.7/lib/python2.7/httplib.py", line 787, in connect
    self.timeout, self.source_address)
  File "/home/trawick/python-2.7/lib/python2.7/socket.py", line 571, in create_connection
    raise err
error: [Errno 110] Connection timed out""".split('\n')

EXPECTED_PYTHON_STACKTRACE = u'1 * [0] Python Exception, Failure was <error: [Errno 110] Connection timed out>\n  get_response, _wrapped_view, index, weather_forecast, around, _fetch, request, _send_request, endheaders, _send_output, send, connect, create_connection, \n'


class TestHttpdLogs(unittest.TestCase):
    def test_describe_python_stacktrace(self):
        self.assertEqual(describe_lines(PYTHON_STACKTRACE), EXPECTED_PYTHON_STACKTRACE)
