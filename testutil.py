"""Unit test utilities.
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

import mox
import pprint
import re
import os
import urlparse
import wsgiref

from google.appengine.api import urlfetch
from google.appengine.ext import testbed
from google.appengine.ext import webapp


class HandlerTest(mox.MoxTestBase):
  """Base test class for webapp2 request handlers.

  Uses App Engine's testbed to set up API stubs:
  http://code.google.com/appengine/docs/python/tools/localunittesting.html

  Attributes:
    application: WSGIApplication
    handler: webapp.RequestHandler
  """

  class UrlfetchResult(object):
    """A fake urlfetch.fetch() result object.
    """
    def __init__(self, status_code, content, headers={}):
      self.status_code = status_code
      self.content = content
      self.headers = headers

  def setUp(self, application=None):
    super(HandlerTest, self).setUp()
    self.application = application

    os.environ['APPLICATION_ID'] = 'app_id'
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_urlfetch_stub()
    self.mox.StubOutWithMock(urlfetch, 'fetch')

    self.setUpHandler()

  def setUpHandler(self, environ=None):
    self.environ = {}
    if environ:
      self.environ.update(environ)
    wsgiref.util.setup_testing_defaults(self.environ)
    self.environ['HTTP_HOST'] = 'HOST'
    self.request = webapp.Request(self.environ)
    self.response = webapp.Response()

    self.handler = webapp.RequestHandler()
    self.handler.initialize(self.request, self.response)

  def expect_urlfetch(self, expected_url, response, status=200, **kwargs):
    """Stubs out urlfetch.fetch() and sets up an expected call.

    Args:
      expected_url: string, regex or mox.Comparator
      response: string
      status: int, HTTP response code
      kwargs: passed to urlfetch.fetch()
    """
    urlfetch.fetch(expected_url, deadline=999, **kwargs).AndReturn(
      self.UrlfetchResult(status, response))

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

  def make_get_request(self, url, expected_status, headers=None):
    """Makes an internal HTTP request for testing.

    Based on bridgy/testutil.py.

    Args:
      method: string, 'GET' or 'POST'
      url: string, the query URL
      expected_status: integer, expected HTTP response status code
      headers: dict of string: string, the HTTP request headers

    Returns:
      webapp.Response
    """
    self.environ['REQUEST_METHOD'] = 'GET'
    parsed = urlparse.urlparse(url)
    self.environ['PATH_INFO'] = parsed.path
    self.environ['QUERY_STRING'] = parsed.query

    if headers:
      datastruct.EnvironHeaders(self.environ).update(headers)

    def start_response(status, headers, exc_info=None):
      assert exc_info is None
      self.assertTrue(status.startswith(str(expected_status)),
                      'Expected %s but was %s' % (expected_status, status))
      self.response.headers = wsgiref.headers.Headers(headers)
      return self.response.out.write

    self.application(self.environ, start_response)
    return self.response
