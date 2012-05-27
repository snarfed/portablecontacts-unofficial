#!/usr/bin/python
"""Unit tests for poco.py.
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

try:
  import json
except ImportError:
  import simplejson as json
from webob import exc

import poco
import source
import source_test
from webutil import testutil


class FakeSource(source.Source):
  contacts = None
  user_id = 0

  def get_contacts(self, user_id=None, start_index=0, count=0):
    if user_id:
      ret = [c for c in self.contacts if c['id'] == user_id]
    else:
      ret = self.contacts

    return len(self.contacts), ret[start_index:count + start_index]

  def get_current_user(self):
    return self.user_id


class HandlersTest(testutil.HandlerTest):

  CONTACTS = [
    {'id': 2, 'displayName': 'me'},
    {'id': 4},
    {'id': 2, 'displayName': 'Ryan'}]
  SELF_CONTACTS = [
    {'id': 2, 'displayName': 'me'},
    {'id': 2, 'displayName': 'Ryan'}]

  def setUp(self):
    super(HandlersTest, self).setUp()
    poco.SOURCE = FakeSource
    poco.SOURCE.contacts = self.CONTACTS
    poco.SOURCE.user_id = 2

  def assert_response(self, url, expected_contacts):
    resp = poco.application.get_response('/poco' + url)
    self.assertEquals(200, resp.status_int)
    self.assert_equals({
        'startIndex': int(resp.request.get('startIndex', 0)),
        'itemsPerPage': len(expected_contacts),
        'totalResults': len(poco.SOURCE.contacts),
        'entry': expected_contacts,
        'filtered': False,
        'sorted': False,
        'updatedSince': False,
        },
      json.loads(resp.body))

  def test_all_no_contacts(self):
    for url in '', '/', '/@me/@all', '/@me/@all/':
      self.setUp()
      poco.SOURCE.contacts = []
      self.assert_response(url, [])

  def test_all_get_some_contacts(self):
    self.assert_response('/@me/@all/', self.CONTACTS)

  def test_self(self):
    self.assert_response('/@me/@self/', self.SELF_CONTACTS)

  def test_user_id(self):
    self.assert_response('/@me/@all/2/', self.SELF_CONTACTS)

  def test_json_format(self):
    self.assert_response('/@me/@all/?format=json', self.CONTACTS)

  def test_xml_format(self):
    resp = poco.application.get_response('/poco/@me/@all/?format=xml')
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

  def test_unknown_format(self):
    resp = poco.application.get_response('/poco/@me/@all/?format=bad')
    self.assertEquals(400, resp.status_int)

  def test_bad_start_index(self):
    resp = poco.application.get_response('/poco/@me/@all/?startIndex=foo')
    self.assertEquals(400, resp.status_int)

  def test_bad_count(self):
    resp = poco.application.get_response('/poco/@me/@all/?count=-1')
    self.assertEquals(400, resp.status_int)

  def test_start_index_count_zero(self):
    self.assert_response('/@me/@all/?startIndex=0&count=0', self.CONTACTS)

  def test_start_index(self):
    self.assert_response('/@me/@all/?startIndex=1&count=0', self.CONTACTS[1:])
    self.assert_response('/@me/@all/?startIndex=2&count=0', self.CONTACTS[2:])

  def test_count_past_end(self):
    self.assert_response('/@me/@all/?startIndex=0&count=10', self.CONTACTS)
    self.assert_response('/@me/@all/?startIndex=1&count=10', self.CONTACTS[1:])

  def test_start_index_past_end(self):
    self.assert_response('/@me/@all/?startIndex=10&count=0', [])
    self.assert_response('/@me/@all/?startIndex=10&count=10', [])

  def test_start_index_subtracts_from_count(self):
    try:
      orig_items_per_page = poco.ITEMS_PER_PAGE
      poco.ITEMS_PER_PAGE = 2
      self.assert_response('/@me/@all/?startIndex=1&count=0', self.CONTACTS[1:2])
    finally:
      poco.ITEMS_PER_PAGE = orig_items_per_page

  def test_start_index_and_count(self):
    self.assert_response('/@me/@all/?startIndex=1&count=1', [self.CONTACTS[1]])
