"""Unit test utilities.
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

import json
import mox
import pprint
import re
import sys
import unittest
import urllib

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import urlfetch
from google.appengine.ext import testbed


class HandlerTest(mox.MoxTestBase):
  """Base test class for webapp2 request handlers.

  Uses App Engine's testbed to set up API stubs:
  http://code.google.com/appengine/docs/python/tools/localunittesting.html

  Attributes:
    app: WSGIApplication
  """

  class UrlfetchResult(object):
    """A fake urlfetch.fetch() result object.
    """
    def __init__(self, status_code, content):
      self.status_code = status_code
      self.content = content

  def setUp(self):
    super(HandlerTest, self).setUp()
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_urlfetch_stub()
    self.mox.StubOutWithMock(urlfetch, 'fetch')

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

  def expect_urlfetch(self, expected_url, response):
    """Stubs out urlfetch.fetch() and sets up an expected call.

    Args:
      expected_url: string, regex or mox.Comparator
      response: string
    """
    # if isinstance(expected_url, mox.Comparator):
    #   comparator = expected_url
    # else:
    #   comparator = mox.Regex(expected_url)

    urlfetch.fetch(expected_url, deadline=999).AndReturn(
      self.UrlfetchResult(200, response))

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
