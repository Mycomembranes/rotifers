#!/usr/bin/env python3
import unittest
from io import StringIO
import sys
from rotifer.core.log import log


class LogTestCase(unittest.TestCase):

    def test_log_outputs_message(self):
        buf = StringIO()
        stderr = sys.stderr
        sys.stderr = buf
        try:
            log({1: 'test message'}, level=1)
        finally:
            sys.stderr = stderr
        self.assertIn('test message', buf.getvalue())

if __name__ == '__main__':
    unittest.main()
