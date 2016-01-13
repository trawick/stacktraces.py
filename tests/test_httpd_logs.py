import io
import json
import os
import unittest

from stacktraces import process_model, thread_analyzer
from stacktraces.analyze import httpd
from stacktraces.native import debugger


class TestHttpdLogs(unittest.TestCase):

    def _test_one_file(self, raw, cooked):
        p = process_model.Process(None)
        dbg = debugger.Debugger(debuglog=io.open(raw, encoding='utf8').readlines(), proc=p)
        dbg.parse()
        thread_analyzer.cleanup(p, httpd.httpd_cleanups)
        thread_analyzer.annotate(p, httpd.httpd_annotations)
        p.group()
        actual = p.description()
        expected = json.loads(io.open(cooked, encoding='utf8').readline())
        self.assertEqual(actual, expected)

    def test_log_files(self):
        for filename in os.listdir('logs/parsed'):
            if filename.endswith('.json'):
                self._test_one_file(os.path.join('logs', filename[:-5]), os.path.join('logs/parsed', filename))

if __name__ == '__main__':
    unittest.main()
