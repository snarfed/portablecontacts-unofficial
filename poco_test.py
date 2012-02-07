#!/usr/bin/python
"""Unit tests for poco.py.
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

import json

import poco
import source
import source_test
import testutil

from google.appengine.ext import webapp


class HandlersTest(testutil.HandlerTest):

  def setUp(self):
    super(HandlersTest, self).setUp()
    poco.APP_ID = 'test'
    poco.SOURCES['test'] = source_test.FakeSource

  def assert_response(self, handler, contacts):
    handler.get()
    self.assertEquals(200, handler.response.status)
    self.assert_equals({
        'startIndex': 0,
        'itemsPerPage': 10,
        'totalResults': len(contacts),
        'entry': contacts,
        },
      json.loads(handler.response.out.getvalue()))

  def test_all_handler_no_contacts(self):
    handler = poco.AllHandler()
    handler.initialize(self.request, self.response)
    handler.source.contacts = []
    self.assert_response(handler, [])

  def test_all_handler_get_some_contacts(self):
    handler = poco.AllHandler()
    handler.initialize(self.request, self.response)
    handler.source.contacts = [{'id': 123}, {'id': 456, 'displayName': 'Ryan'}]
    self.assert_response(handler, handler.source.contacts)

  def test_self_handler(self):
    handler = poco.SelfHandler()
    handler.initialize(self.request, self.response)
    handler.source.user_id = 9
    handler.source.contacts = [{'id': 123}, {'id': 9, 'displayName': 'Ryan'}]
    self.assert_response(handler, [{'id': 9, 'displayName': 'Ryan'}])

  def test_user_id_handler(self):
    self.environ['PATH_INFO'] = '/poco/@me/456/'
    handler = poco.UserIdHandler()
    handler.initialize(self.request, self.response)
    handler.source.contacts = [{'id': 123}, {'id': 456, 'displayName': 'Ryan'}]
    self.assert_response(handler, [{'id': 456, 'displayName': 'Ryan'}])
