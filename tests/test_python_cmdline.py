import unittest

import pytz
import six

from stacktraces.python.shortcuts import describe_lines, parse_trace_msg, process_log_file, read_log

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
error: [Errno 110] Connection timed out""".split('\n')  # noqa

EXPECTED_PYTHON_STACKTRACE = (
    u'1 * [0] Failure was <error: [Errno 110] Connection timed out>\n  get_response, ' +
    u'_wrapped_view, index, weather_forecast, around, _fetch, request, _send_request, endheaders, ' +
    u'_send_output, send, connect, create_connection, \n'
)


class TestPythonStacktrace(unittest.TestCase):
    def test_describe_python_stacktrace(self):
        self.assertEqual(describe_lines(PYTHON_STACKTRACE), EXPECTED_PYTHON_STACKTRACE)


LOG_FILE_CONTENTS = u"""
[14/Mar/2015 01:37:05] ERROR [django.request:231] Internal Server Error: /walk/ExYu
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
error: [Errno 110] Connection timed out

"""  # noqa

LOG_FILE_CONTENTS_2 = u"""
[something-before-exception]
Traceback (most recent call last):
  File "/home/trawick/foo2.py", line 22, in <module>
    a()
  File "/home/trawick/foo2.py", line 18, in a
    b()
  File "/home/trawick/foo2.py", line 14, in b
    c()
  File "/home/trawick/foo2.py", line 10, in c
    d()
  File "/home/trawick/foo2.py", line 6, in d
    raise ValueError('aaa')
ValueError: aaa
bbb
ccc
[something-after-exception]
"""  # noqa

LOG_FILE_CONTENTS_3 = u"""
[25/Dec/2015 12:59:55] ERROR [django.request:231] Internal Server Error: /admin/walks/walk/add/
Traceback (most recent call last):
  File "/home/trawick/git/walking/envs/walking/local/lib/python2.7/site-packages/django/core/handlers/base.py", line 111, in get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
  File "/home/trawick/git/walking/envs/walking/local/lib/python2.7/site-packages/django/contrib/admin/options.py", line 583, in wrapper
    return self.admin_site.admin_view(view)(*args, **kwargs)
  File "/home/trawick/git/walking/envs/walking/local/lib/python2.7/site-packages/django/utils/decorators.py", line 105, in _wrapped_view
    response = view_func(request, *args, **kwargs)
  File "/home/trawick/git/walking/envs/walking/local/lib/python2.7/site-packages/django/views/decorators/cache.py", line 52, in _wrapped_view_func
    response = view_func(request, *args, **kwargs)
  File "/home/trawick/git/walking/envs/walking/local/lib/python2.7/site-packages/django/contrib/admin/sites.py", line 206, in inner
    return view(request, *args, **kwargs)
  File "/home/trawick/git/walking/envs/walking/local/lib/python2.7/site-packages/django/contrib/admin/options.py", line 1453, in add_view
    return self.changeform_view(request, None, form_url, extra_context)
  File "/home/trawick/git/walking/envs/walking/local/lib/python2.7/site-packages/django/utils/decorators.py", line 29, in _wrapper
    return bound_func(*args, **kwargs)
  File "/home/trawick/git/walking/envs/walking/local/lib/python2.7/site-packages/django/utils/decorators.py", line 105, in _wrapped_view
    response = view_func(request, *args, **kwargs)
  File "/home/trawick/git/walking/envs/walking/local/lib/python2.7/site-packages/django/utils/decorators.py", line 25, in bound_func
    return func.__get__(self, type(self))(*args2, **kwargs2)
  File "/home/trawick/git/walking/envs/walking/local/lib/python2.7/site-packages/django/db/transaction.py", line 394, in inner
    return func(*args, **kwargs)
  File "/home/trawick/git/walking/envs/walking/local/lib/python2.7/site-packages/django/contrib/admin/options.py", line 1404, in changeform_view
    self.save_model(request, new_object, form, not add)
  File "/home/trawick/git/walking/envs/walking/local/lib/python2.7/site-packages/django/contrib/admin/options.py", line 1045, in save_model
    obj.save()
  File "/home/trawick/git/walking/envs/walking/local/lib/python2.7/site-packages/django/db/models/base.py", line 589, in save
    force_update=force_update, update_fields=update_fields)
  File "/home/trawick/git/walking/envs/walking/local/lib/python2.7/site-packages/django/db/models/base.py", line 617, in save_base
    updated = self._save_table(raw, cls, force_insert, force_update, using, update_fields)
  File "/home/trawick/git/walking/envs/walking/local/lib/python2.7/site-packages/django/db/models/base.py", line 698, in _save_table
    result = self._do_insert(cls._base_manager, using, fields, update_pk, raw)
  File "/home/trawick/git/walking/envs/walking/local/lib/python2.7/site-packages/django/db/models/base.py", line 731, in _do_insert
    using=using, raw=raw)
  File "/home/trawick/git/walking/envs/walking/local/lib/python2.7/site-packages/django/db/models/manager.py", line 92, in manager_method
    return getattr(self.get_queryset(), name)(*args, **kwargs)
  File "/home/trawick/git/walking/envs/walking/local/lib/python2.7/site-packages/django/db/models/query.py", line 921, in _insert
    return query.get_compiler(using=using).execute_sql(return_id)
  File "/home/trawick/git/walking/envs/walking/local/lib/python2.7/site-packages/django/db/models/sql/compiler.py", line 920, in execute_sql
    cursor.execute(sql, params)
  File "/home/trawick/git/walking/envs/walking/local/lib/python2.7/site-packages/django/db/backends/utils.py", line 65, in execute
    return self.cursor.execute(sql, params)
  File "/home/trawick/git/walking/envs/walking/local/lib/python2.7/site-packages/django/db/utils.py", line 94, in __exit__
    six.reraise(dj_exc_type, dj_exc_value, traceback)
  File "/home/trawick/git/walking/envs/walking/local/lib/python2.7/site-packages/django/db/backends/utils.py", line 65, in execute
    return self.cursor.execute(sql, params)
IntegrityError: duplicate key value violates unique constraint "walks_walk_walk_group_id_key"
DETAIL:  Key (walk_group_id, walk_datetime)=(ExYu, 2016-01-10 14:30:00+00) already exists.

"""  # noqa

LOG_FILE_CONTENTS_4 = u"""
[09/Sep/2014 23:45:54] INFO [requests.packages.urllib3.connectionpool:188] Starting new HTTP connection (1): edjective.org
[10/Sep/2014 00:11:01] INFO [requests.packages.urllib3.connectionpool:188] Starting new HTTP connection (1): www.fit-ed.org
[10/Sep/2014 02:11:01] INFO [requests.packages.urllib3.connectionpool:188] Starting new HTTP connection (1): www.fit-ed.org
[10/Sep/2014 04:11:02] INFO [requests.packages.urllib3.connectionpool:188] Starting new HTTP connection (1): www.fit-ed.org
[10/Sep/2014 13:43:32] ERROR [django.request:224] Internal Server Error: /ed/resources/42/
Traceback (most recent call last):
  File "/home/trawick/git/edurepo/envs/edurepo/lib/python2.7/site-packages/django/core/handlers/base.py", line 112, in get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
  File "/home/trawick/git/edurepo/src/edurepo/resources/views.py", line 21, in detail
    resource = Resource.objects.get(id=resource_id)
  File "/home/trawick/git/edurepo/envs/edurepo/lib/python2.7/site-packages/django/db/models/manager.py", line 151, in get
    return self.get_queryset().get(*args, **kwargs)
  File "/home/trawick/git/edurepo/envs/edurepo/lib/python2.7/site-packages/django/db/models/query.py", line 310, in get
    self.model._meta.object_name)
DoesNotExist: Resource matching query does not exist.
[10/Sep/2014 13:43:32] ERROR [django.request:224] Internal Server Error: /ed/resources/42/
Traceback (most recent call last):
  File "/home/trawick/git/edurepo/envs/edurepo/lib/python2.7/site-packages/django/core/handlers/base.py", line 112, in get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
  File "/home/trawick/git/edurepo/src/edurepo/resources/views.py", line 21, in detail
    resource = Resource.objects.get(id=resource_id)
  File "/home/trawick/git/edurepo/envs/edurepo/lib/python2.7/site-packages/django/db/models/manager.py", line 151, in get
    return self.get_queryset().get(*args, **kwargs)
  File "/home/trawick/git/edurepo/envs/edurepo/lib/python2.7/site-packages/django/db/models/query.py", line 310, in get
    self.model._meta.object_name)
DoesNotExist: Resource matching query does not exist.
[10/Sep/2014 13:43:32] ERROR [django.request:224] Internal Server Error: /ed/resources/42/
Traceback (most recent call last):
  File "/home/trawick/git/edurepo/envs/edurepo/lib/python2.7/site-packages/django/core/handlers/base.py", line 112, in get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
  File "/home/trawick/git/edurepo/src/edurepo/resources/views.py", line 21, in detail
    resource = Resource.objects.get(id=resource_id)
  File "/home/trawick/git/edurepo/envs/edurepo/lib/python2.7/site-packages/django/db/models/manager.py", line 151, in get
    return self.get_queryset().get(*args, **kwargs)
  File "/home/trawick/git/edurepo/envs/edurepo/lib/python2.7/site-packages/django/db/models/query.py", line 310, in get
    self.model._meta.object_name)
DoesNotExist: Resource matching query does not exist.
[10/Sep/2014 16:39:37] ERROR [django.request:224] Internal Server Error: /ed/resources/31/
Traceback (most recent call last):
  File "/home/trawick/git/edurepo/envs/edurepo/lib/python2.7/site-packages/django/core/handlers/base.py", line 112, in get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
  File "/home/trawick/git/edurepo/src/edurepo/resources/views.py", line 21, in detail
    resource = Resource.objects.get(id=resource_id)
  File "/home/trawick/git/edurepo/envs/edurepo/lib/python2.7/site-packages/django/db/models/manager.py", line 151, in get
    return self.get_queryset().get(*args, **kwargs)
  File "/home/trawick/git/edurepo/envs/edurepo/lib/python2.7/site-packages/django/db/models/query.py", line 310, in get
    self.model._meta.object_name)
DoesNotExist: Resource matching query does not exist.
[10/Sep/2014 16:39:37] ERROR [django.request:224] Internal Server Error: /ed/resources/31/
Traceback (most recent call last):
  File "/home/trawick/git/edurepo/envs/edurepo/lib/python2.7/site-packages/django/core/handlers/base.py", line 112, in get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
  File "/home/trawick/git/edurepo/src/edurepo/resources/views.py", line 21, in detail
    resource = Resource.objects.get(id=resource_id)
  File "/home/trawick/git/edurepo/envs/edurepo/lib/python2.7/site-packages/django/db/models/manager.py", line 151, in get
    return self.get_queryset().get(*args, **kwargs)
  File "/home/trawick/git/edurepo/envs/edurepo/lib/python2.7/site-packages/django/db/models/query.py", line 310, in get
    self.model._meta.object_name)
DoesNotExist: Resource matching query does not exist.
[10/Sep/2014 16:39:37] ERROR [django.request:224] Internal Server Error: /ed/resources/31/
Traceback (most recent call last):
  File "/home/trawick/git/edurepo/envs/edurepo/lib/python2.7/site-packages/django/core/handlers/base.py", line 112, in get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
  File "/home/trawick/git/edurepo/src/edurepo/resources/views.py", line 21, in detail
    resource = Resource.objects.get(id=resource_id)
  File "/home/trawick/git/edurepo/envs/edurepo/lib/python2.7/site-packages/django/db/models/manager.py", line 151, in get
    return self.get_queryset().get(*args, **kwargs)
  File "/home/trawick/git/edurepo/envs/edurepo/lib/python2.7/site-packages/django/db/models/query.py", line 310, in get
    self.model._meta.object_name)
DoesNotExist: Resource matching query does not exist.
"""  # noqa


def file_from_string(contents):
    if six.PY2:
        import StringIO
        logfile = StringIO.StringIO(contents)
    else:
        import io
        logfile = io.StringIO(contents)
    return logfile


def output_to_string():
    if six.PY2:
        import StringIO
        return StringIO.StringIO()
    else:
        import io
        return io.StringIO()


class TestPythonLog(unittest.TestCase):
    def test_simple_logfile(self):
        logfile = file_from_string(LOG_FILE_CONTENTS)
        output_buffer = []
        for p, traceback_lines in read_log(tracelvl=1, logfile=logfile):
            output_buffer.append(six.text_type(p))

        expected = u"""1 * [0] Failure was <error: [Errno 110] Connection timed out>, at <14/Mar/2015 01:37:05>
  get_response, _wrapped_view, index, weather_forecast, around, _fetch, request, _send_request, endheaders, _send_output, send, connect, create_connection, \n"""  # noqa
        self.assertEqual(output_buffer, [expected])

    def test_another_logfile(self):
        logfile = file_from_string(LOG_FILE_CONTENTS_2)
        output_buffer = []
        for p, traceback_lines in read_log(tracelvl=1, logfile=logfile):
            output_buffer.append(six.text_type(p))

        expected = u"""1 * [0] Failure was <ValueError: aaa|bbb|ccc>\n  <module>, a, b, c, d, \n"""  # noqa
        self.assertEqual(output_buffer, [expected])

    def test_yet_another_logfile(self):
        logfile = file_from_string(LOG_FILE_CONTENTS_3)
        output_buffer = []
        for p, traceback_lines in read_log(tracelvl=1, logfile=logfile):
            output_buffer.append(six.text_type(p))

        expected = u"""1 * [0] Failure was <IntegrityError: duplicate key value violates unique constraint "walks_walk_walk_group_id_key"|DETAIL:  Key (walk_group_id, walk_datetime)=(ExYu, 2016-01-10 14:30:00+00) already exists.>, at <25/Dec/2015 12:59:55>\n  get_response, wrapper, _wrapped_view, _wrapped_view_func, inner, add_view, _wrapper, _wrapped_view, bound_func, inner, changeform_view, save_model, save, save_base, _save_table, _do_insert, manager_method, _insert, execute_sql, execute, __exit__, execute, \n"""  # noqa
        self.assertEqual(output_buffer, [expected])

    def test_parse_trace_msg(self):
        us_eastern = pytz.timezone('US/Eastern')
        tests = [
            [
                '2014-03-06 16:29:21 [4354] [INFO] Worker exiting (pid: 4354)',
                us_eastern,
                'Worker exiting (pid: 4354)',
                '2014-03-06 16:29:21',
                '2014-03-06T16:29:21-05:00',
            ],
            [
                # same as previous, but no time zone information
                '2014-03-06 16:29:21 [4354] [INFO] Worker exiting (pid: 4354)',
                None,
                'Worker exiting (pid: 4354)',
                '2014-03-06 16:29:21',
                '2014-03-06T16:29:21',
            ],
            [
                '[anything]any-other-thing',
                us_eastern,
                'any-other-thing',
                None,
                None
            ],
            [
                '[14/Mar/2015 01:37:05] ERROR [django.request:231] Internal Server Error: /walk/ExYu',
                us_eastern,
                'Internal Server Error: /walk/ExYu',
                '14/Mar/2015 01:37:05',
                '2015-03-14T01:37:05-04:00'
            ],
            [
                '', None, None, None, None,
            ],
            [
                'anything', None, None, None, None,
            ],
            [
                '[pid: 10876|app: 0|req: 7/7] 45.37.54.3 () {70 vars in 3333 bytes} [Sat Apr 18 21:34:03 2015] GET /walk/ExYu => generated 6134 bytes in 1257 msecs (HTTP/1.1 200) 4 headers in 223 bytes (1 switches on core 0)',  # noqa
                us_eastern,
                'GET /walk/ExYu => generated 6134 bytes in 1257 msecs (HTTP/1.1 200) 4 headers in 223 bytes (1 switches on core 0)',  # noqa
                'Sat Apr 18 21:34:03 2015',
                '2015-04-18T21:34:03-04:00',
            ],
            [
                '2015-03-08 12:13:35,086 projectname WARNING Foomessage',
                us_eastern,
                'Foomessage',
                '2015-03-08 12:13:35,086',
                '2015-03-08T12:13:35.086000-04:00',
            ],
            [
                # same as previous, but no milliseconds with timestamp
                '2015-03-08 12:13:35 projectname WARNING Foomessage',
                us_eastern,
                'Foomessage',
                '2015-03-08 12:13:35',
                '2015-03-08T12:13:35-04:00',
            ]
        ]

        for log_line, pytz_timezone, expected_msg, expected_timestamp, expected_isodt in tests:
            actual_msg, actual_timestamp, dt = parse_trace_msg(log_line, pytz_timezone)
            self.assertEqual(expected_timestamp, actual_timestamp)
            self.assertEqual(expected_msg, actual_msg)
            self.assertEqual(bool(dt), bool(expected_isodt), 'Basic timestamp issue with %s' % log_line)
            if dt:
                self.assertEqual(expected_isodt, dt.isoformat())

            # Try again with newline at end of message
            actual_msg, actual_timestamp, dt = parse_trace_msg(log_line + '\n', pytz_timezone)
            self.assertEqual(expected_timestamp, actual_timestamp)
            self.assertEqual(expected_msg, actual_msg)
            if dt:
                self.assertEqual(expected_isodt, dt.isoformat())

    def test_high_level_log_api(self):
        single_error_message = u'DoesNotExist: Resource matching query does not exist.'
        single_stacktrace = u'get_response, detail, get, get'
        output_string = output_to_string()
        message_counts, stacktrace_counts = process_log_file(
            file_from_string(LOG_FILE_CONTENTS_4),
            output_string,
            output_format='text',
            include_duplicates=False,
            include_raw=False,
        )
        self.assertEqual(
            single_error_message + u'\nget_response, detail, get, get\n\n',
            output_string.getvalue()
        )
        self.assertEqual([single_error_message], list(message_counts.keys()))
        self.assertEqual(6, message_counts[single_error_message])
        self.assertEqual([single_stacktrace], list(stacktrace_counts.keys()))
        self.assertEqual(6, stacktrace_counts[single_stacktrace])
