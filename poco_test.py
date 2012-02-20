#!/usr/bin/python
"""Unit tests for poco.py.

STATE: testing xml
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

  CONTACTS = [
    {'id': 2, 'displayName': 'me'},
    {'id': 4},
    {'id': 2, 'displayName': 'Ryan'}]
  SELF_CONTACTS = [
    {'id': 2, 'displayName': 'me'},
    {'id': 2, 'displayName': 'Ryan'}]

  def setUp(self):
    super(HandlersTest, self).setUp(application=poco.application)
    poco.SOURCE = source_test.FakeSource
    poco.SOURCE.contacts = self.CONTACTS
    poco.SOURCE.user_id = 2

  def assert_response(self, path, expected_contacts, **kwargs):
    resp = self.make_get_request(path, 200, **kwargs)
    self.assert_equals({
        'startIndex': 0,
        'itemsPerPage': 10,
        'totalResults': len(expected_contacts),
        'entry': expected_contacts,
        },
      json.loads(resp.out.getvalue()))

  def test_all_no_contacts(self):
    for url in '/poco', '/poco/', '/poco/@me/@all', '/poco/@me/@all/':
      self.setUp()
      poco.SOURCE.contacts = []
      self.assert_response(url, [])

  def test_all_get_some_contacts(self):
    self.assert_response('/poco/@me/@all/', self.CONTACTS)

  def test_self(self):
    self.assert_response('/poco/@me/@self/', self.SELF_CONTACTS)

  def test_user_id(self):
    self.assert_response('/poco/@me/@all/2/', self.SELF_CONTACTS)

  def test_json_format(self):
    self.assert_response('/poco/@me/@all/?format=json', self.CONTACTS)

  def test_xml_format(self):
    resp = self.make_get_request('/poco/@me/@all/?format=xml', 200)
    self.assertEqual("""\
<?xml version="1.0" encoding="UTF-8"?>
<response>
<totalResults>3</totalResults>
<startIndex>0</startIndex>
<itemsPerPage>10</itemsPerPage>
<entry>
<displayName>me</displayName>
<id>2</id>
</entry>
<entry>
<id>4</id>
</entry>
<entry>
<displayName>Ryan</displayName>
<id>2</id>
</entry>
</response>
""", resp.out.getvalue())

  def test_unknown_format(self):
    self.make_get_request('/poco/@me/@all/?format=bad', 400)
