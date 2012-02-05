"""Unit test utilities.
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

import json
import pprint
import re
import sys
import unittest
import urllib


class HandlerTest(unittest.TestCase):
  """Base test class for webapp2 request handlers.

  Attributes:
    app: WSGIApplication
  """

  # def setUp(self, *handler_classes):
  #   """Args:
  #   handler_classes: RequestHandlers to initialize
  #   """
  #   super(HandlerTest, self).setUp()
  #   self.app = server.application()

  # def expect(self, path, expected, args=None, expected_status=200):
  #   """Makes a request and checks the response.

  #   Args:
  #     path: string
  #     expected: if string, the expected response body. if list or dict,
  #       the expected JSON response contents.
  #     args: passed to get_response()
  #     expected_status: integer, expected HTTP response status
  #   """
  #   response = None
  #   results = None
  #   try:
  #     response = self.get_response(path, args=args)
  #     self.assertEquals(expected_status, response.status_int)
  #     response = response.body
  #     if isinstance(expected, basestring):
  #       self.assertEquals(expected, response)
  #     else:
  #       results = json.loads(response)
  #       if not isinstance(expected, list):
  #         expected = [expected]
  #       if not isinstance(results, list):
  #         results = [results]
  #       expected.sort()
  #       results.sort()
  #       self.assertEquals(len(expected), len(results), `expected, results`)
  #       for e, r in zip(expected, results):
  #         self.assert_dict_equals(e, r)
  #   except:
  #     print >> sys.stderr, '\nquery: %s %s' % (path, args)
  #     print >> sys.stderr, 'expected: %r' % expected
  #     print >> sys.stderr, 'received: %r' % results if results else response
  #     raise

  # def get_response(self, path, args=None):
  #   if args:
  #     path = '%s?%s' % (path, urllib.urlencode(args))
  #   return self.app.get_response(path)

  def assert_equals(self, expected, actual):
    """Pinpoints individual element differences in lists and dicts.

    Ignores order in lists.
    """
    try:
      self._assert_equals(expected, actual)
    except AssertionError, e:
      raise AssertionError(''.join(e.args) + '\nActual value:\n' +
                           pprint.pformat(actual))

  def _assert_equals(self, expected, actual):
    """Recursive helper for assert_equals().
    """
    key = None

    try:
      if isinstance(expected, re._pattern_type):
        if not re.match(expected, actual):
          self.fail("%r doesn't match %s" % (expected, actual))
      elif isinstance(expected, dict) and isinstance(actual, dict):
        for key in set(expected.keys()) | set(actual.keys()):
          self._assert_equals(expected.get(key), actual.get(key))
      elif isinstance(expected, (list, tuple)) and isinstance(actual, (list, tuple)):
        expected = sorted(list(expected))
        actual = sorted(list(actual))
        for key, (e, a) in enumerate(zip(expected, actual)):
          self._assert_equals(e, a)
      else:
        self.assertEquals(expected, actual)

    except AssertionError, e:
      # fill in where this failure came from. this recursively builds,
      # backwards, all the way up to the root.
      args = ('[%s] ' % key if key is not None else '') + ''.join(e.args)
      raise AssertionError(args)
