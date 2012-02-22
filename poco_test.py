#!/usr/bin/python
"""Unit tests for poco.py.

STATE: testing xml
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

try:
  import json
except ImportError:
  import simplejson as json
import mox
from webob import exc

import poco
import source
import source_test
import testutil


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

  def assert_response(self, url, expected_contacts):
    resp = self.application.get_response(url)
    self.assertEquals(200, resp.status_int)
    self.assert_equals({
        'startIndex': 0,
        'itemsPerPage': 3,
        'totalResults': len(expected_contacts),
        'entry': expected_contacts,
        'filtered': False,
        'sorted': False,
        'updatedSince': False,
        },
      json.loads(resp.body))

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
    resp = self.application.get_response('/poco/@me/@all/?format=xml')
    self.assertEquals(200, resp.status_int)
    self.assertEqual("""\
<?xml version="1.0" encoding="UTF-8"?>
<response>
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
<itemsPerPage>3</itemsPerPage>
<updatedSince>False</updatedSince>
<startIndex>0</startIndex>
<sorted>False</sorted>
<filtered>False</filtered>
<totalResults>3</totalResults>
</response>
""", resp.body)

  def test_pass_through_start_index_and_count(self):
    self.mox.StubOutWithMock(poco.SOURCE, 'get_contacts')
    poco.SOURCE.get_contacts(None, startIndex=2, count=4).AndReturn([])
    self.mox.ReplayAll()
    self.application.get_response('/poco/@me/@all/?startIndex=2&count=4')

  def test_bad_start_index(self):
    resp = self.application.get_response('/poco/@me/@all/?startIndex=foo')
    self.assertEquals(400, resp.status_int)

  def test_bad_count(self):
    resp = self.application.get_response('/poco/@me/@all/?count=-1')
    self.assertEquals(400, resp.status_int)

  def test_unknown_format(self):
    resp = self.application.get_response('/poco/@me/@all/?format=bad')
    self.assertEquals(400, resp.status_int)
