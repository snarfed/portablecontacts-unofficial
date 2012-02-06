#!/usr/bin/python
"""Unit tests for poco.py.
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

import json
import mox
import unittest

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


  # def test_get_contacts_user_id(self):
  #   self.expect_urlfetch(
  #     'https://api.twitter.com/1/followers/ids.json?user_id=123',
  #     json.dumps({'ids': []}))
  #   self.mox.ReplayAll()

  #   self.assert_equals({
  #       'startIndex': 0,
  #       'itemsPerPage': 10,
  #       'totalResults': 2,
  #       'entry': [],
  #       },
  #   self.handler.get_contacts(user_id=123))
