#!/usr/bin/python
"""Unit tests for poco.py.
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

from webob import exc

import source
import testutil


class FakeSource(source.Source):
  contacts = None
  user_id = 0

  def get_contacts(self, user_id=None):
    return self.contacts

  def get_current_user_id(self):
    return self.user_id


class SourceTest(testutil.HandlerTest):
  def setUp(self):
    super(SourceTest, self).setUp()
    self.source = FakeSource(self.handler)

  def test_urlfetch(self):
    self.expect_urlfetch('http://my/url', 'hello', foo='bar')
    self.mox.ReplayAll()
    self.assertEquals('hello', self.source.urlfetch('http://my/url', foo='bar'))

  def test_urlfetch_error_passes_through(self):
    self.expect_urlfetch('http://my/url', 'my error', status=408)
    self.mox.ReplayAll()

    try:
      self.source.urlfetch('http://my/url')
    except exc.HTTPException, e:
      self.assertEquals(408, e.status_int)
      self.assertEquals('my error', self.response.out.getvalue())
