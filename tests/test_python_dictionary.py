import unittest

from stacktraces.python.shortcuts import get_process_from_traceback

PYTHON_STACKTRACE_1 = u"""[14/Mar/2015 01:37:05] ERROR [django.request:231] Internal Server Error: /walk/ExYu
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
error: [Errno 110] Connection timed out""".split('\n')  # noqa

EXPECTED_DICT_1 = {
    'processname': 'no-name',
    'threadgroups': [{'thread_ids': [0]}],
    'threads': [
        {
            'failure': u'error: [Errno 110] Connection timed out',
            'frames': [
                {'fn': u'get_response', 'id': 1},
                {'fn': u'_wrapped_view', 'id': 2},
                {'fn': u'index', 'id': 3},
                {'fn': u'weather_forecast', 'id': 4},
                {'fn': u'around', 'id': 5},
                {'fn': u'_fetch', 'id': 6},
                {'fn': u'request', 'id': 7},
                {'fn': u'_send_request', 'id': 8},
                {'fn': u'endheaders', 'id': 9},
                {'fn': u'_send_output', 'id': 10},
                {'fn': u'send', 'id': 11},
                {'fn': u'connect', 'id': 12},
                {'fn': u'create_connection', 'id': 13}
            ],
        }
    ]
}

PYTHON_STACKTRACE_2 = u"""Could not interpret 500 /proxy/data/2.5/forecast?mode=json&lat=35.83&cnt=1&lon=-78.75& as json
Traceback (most recent call last):
  File "/home/trawick/git/walking/src/walking/walking/weather.py", line 50, in _fetch
    d = json.loads(json_rsp)
  File "/home/trawick/python-2.7/lib/python2.7/json/__init__.py", line 338, in loads
    return _default_decoder.decode(s)
  File "/home/trawick/python-2.7/lib/python2.7/json/decoder.py", line 369, in decode
    raise ValueError(errmsg("Extra data", s, end, len(s)))
ValueError: Extra data: line 2 column 1 - line 3 column 1 (char 4 - 67)""".split('\n')  # noqa

EXPECTED_DICT_2 = {
    'processname': 'no-name',
    'threadgroups': [{'thread_ids': [0]}],
    'threads': [
        {
            'failure': u'ValueError: Extra data: line 2 column 1 - line 3 column 1 (char 4 - 67)',
            'frames': [
                {'fn': u'_fetch', 'id': 1},
                {'fn': u'loads', 'id': 2},
                {'fn': u'decode', 'id': 3}
            ],
        }
    ]
}

EXPECTED_DICT_2_W = {
    'mv': 1,
    'process': {
        'processname': 'no-name',
        'threadgroups': [{'thread_ids': [0]}],
        'threads': [
            {
                'failure': u'ValueError: Extra data: line 2 column 1 - line 3 column 1 (char 4 - 67)',
                'frames': [
                    {'fn': u'_fetch', 'id': 1},
                    {'fn': u'loads', 'id': 2},
                    {'fn': u'decode', 'id': 3}
                ],
            }
        ]
    }
}


class TestPythonParsing(unittest.TestCase):

    def test(self):
        self.maxDiff = None
        p = get_process_from_traceback(PYTHON_STACKTRACE_1)
        self.assertEqual(EXPECTED_DICT_1, p.description(),)

        p = get_process_from_traceback(PYTHON_STACKTRACE_2)
        self.assertEqual(EXPECTED_DICT_2, p.description(),)

        self.assertEqual(EXPECTED_DICT_2_W, p.description(wrapped=True))


if __name__ == '__main__':
    unittest.main()
