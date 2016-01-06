import io
import json
import os
import unittest

import debugger
import httpd
import process_model
import thread_analyzer


class TestHttpdLogs(unittest.TestCase):

    def _test_one_file(self, raw, cooked):
        p = process_model.Process(None)
        dbg = debugger.Debugger(debuglog=io.open(raw, encoding='utf8').readlines(), proc=p)
        dbg.parse()
        thread_analyzer.cleanup(p, httpd.httpd_cleanups)
        thread_analyzer.annotate(p, httpd.httpd_annotations)
        p.group()
        actual = json.dumps(p.description())
        expected = io.open(cooked, encoding='utf8').readline()
        self.assertEqual(actual.strip(), expected.strip())

    def test_log_files(self):
        for filename in os.listdir('logs/parsed'):
            if filename.endswith('.json'):
                self._test_one_file(os.path.join('logs', filename[:-5]), os.path.join('logs/parsed', filename))

if __name__ == '__main__':
    unittest.main()
