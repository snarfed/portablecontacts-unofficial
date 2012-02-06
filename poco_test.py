#!/usr/bin/python
"""Unit tests for poco.py.
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

import json
import mox
import unittest

from webob import exc

import poco
import testutil

from google.appengine.ext import webapp


class FakeHandler(poco.PocoHandler):
  contacts = None

  def get_contacts(self, user_id=None, username=None):
    return self.contacts


class PocoHandlerTest(testutil.HandlerTest):

  def setUp(self):
    super(PocoHandlerTest, self).setUp()
    self.handler = FakeHandler()
    self.handler.initialize(self.request, self.response)

  def test_get_no_contacts(self):
    self.handler.contacts = []
    self.handler.get()

    self.assertEquals(200, self.response.status)
    self.assert_equals({
        'startIndex': 0,
        'itemsPerPage': 10,
        'totalResults': 0,
        'entry': self.handler.contacts,
        },
      json.loads(self.response.out.getvalue()))

  def test_get_some_contacts(self):
    self.handler.contacts = [{'id': 123}, {'id': 456, 'displayName': 'Ryan'}]
    self.handler.get()

    self.assertEquals(200, self.response.status)
    self.assert_equals({
        'startIndex': 0,
        'itemsPerPage': 10,
        'totalResults': 2,
        'entry': self.handler.contacts,
        },
      json.loads(self.response.out.getvalue()))

  def test_urlfetch(self):
    self.expect_urlfetch('http://my/url', 'hello', foo='bar')
    self.mox.ReplayAll()
    self.assertEquals('hello', self.handler.urlfetch('http://my/url', foo='bar'))

  def test_urlfetch_error_passes_through(self):
    self.expect_urlfetch('http://my/url', 'my error', status=408)
    self.mox.ReplayAll()

    try:
      self.handler.urlfetch('http://my/url')
    except exc.HTTPException, e:
      self.assertEquals(408, e.status_int)
      self.assertEquals('my error', self.response.out.getvalue())
