#!/usr/bin/python
"""Unit tests for poco.py.
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

import json
import webob

import poco
import source
import source_test
import testutil

from google.appengine.ext import webapp


# # bleh, ugly. webob.Request url-encodes request paths by default, which converts
# # @ to %40. we use @ in URL mappings in poco.py, e.g. /poco/@me/@all/, which
# # don't match %40.
# #
# # oddly though, webob.Request only does that url encoding in unit tests, *not*
# # in dev_appserver or prod. so, monkey patch it here to not url encode.
# webob.Request.path = property(lambda self: self.script_name + self.path_info)


class HandlersTest(testutil.HandlerTest):

  def setUp(self):
    super(HandlersTest, self).setUp(application=poco.application)
    poco.SOURCE = source_test.FakeSource

  def assert_response(self, path, expected_contacts):
    resp = self.make_get_request(path, 200)
    self.assert_equals({
        'startIndex': 0,
        'itemsPerPage': 10,
        'totalResults': len(expected_contacts),
        'entry': expected_contacts,
        },
      json.loads(resp.out.getvalue()))

  def test_all_no_contacts(self):
    poco.SOURCE.contacts = []
    for url in '/poco', '/poco/', '/poco/@me/@all', '/poco/@me/@all/':
      self.setUp()
      self.assert_response(url, [])

  def test_all_get_some_contacts(self):
    poco.SOURCE.contacts = [{'id': 123}, {'id': 456, 'displayName': 'Ryan'}]
    self.assert_response('/poco/@me/@all/', poco.SOURCE.contacts)

  def test_self(self):
    poco.SOURCE.user_id = 9
    poco.SOURCE.contacts = [{'id': 9, 'displayName': 'me'},
                            {'id': 123},
                            {'id': 9, 'displayName': 'Ryan'},
                            ]
    self.assert_response('/poco/@me/@self/',
                         [{'id': 9, 'displayName': 'me'},
                          {'id': 9, 'displayName': 'Ryan'}])

  def test_user_id(self):
    poco.SOURCE.contacts = [{'id': 456, 'displayName': 'other'},
                            {'id': 123},
                            {'id': 456, 'displayName': 'Foo'},
                            ]
    self.assert_response('/poco/@me/@all/456/',
                         [{'id': 456, 'displayName': 'other'},
                          {'id': 456, 'displayName': 'Foo'},
                          ])
