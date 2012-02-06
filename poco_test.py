#!/usr/bin/python
"""Unit tests for poco.py.
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

import json
import mox
import unittest

import testutil

from google.appengine.ext import webapp


class PocoHandlerTest(testutil.HandlerTest):
  pass
  # def test_get_contacts_username(self):
  #   self.expect_urlfetch(
  #     'https://api.twitter.com/1/followers/ids.json?screen_name=username',
  #     '{"ids": [123, 456]}')
  #   self.expect_urlfetch(
  #     'https://api.twitter.com/1/users/lookup.json?user_id=123,456',
  #     json.dumps([{
  #         'id': 123,
  #         'screen_name': 'foo',
  #         'name': 'Mr. Foo',
  #         'location': 'Hometown',
  #         'url': 'http://foo.com/',
  #         'profile_image_url': 'http://foo.com/pic.jpg',
  #         }, {
  #         'id': 456,
  #         'name': 'Ms. Bar',
  #         }]))
  #   self.expect_urlfetch(
  #     'https://api.twitter.com/1/users/lookup.json?user_id=456',
  #     '{"ids": [123, 456]}')
  #   self.mox.ReplayAll()

  #   self.assert_equals({
  #       'startIndex': 0,
  #       'itemsPerPage': 10,
  #       'totalResults': 2,
  #       'entry': [{
  #           'id': '123',
  #           'displayName': 'Mr. Foo',
  #           'name': {'formatted': 'Mr. Foo'},
  #           'accounts': [{'domain': 'twitter.com',
  #                         'userid': '123',
  #                         'username': 'foo'}],
  #           'addresses': [{'formatted': 'Hometown', 'type': 'home'}],
  #           'photos': [{'value': 'http://foo.com/pic.jpg', 'primary': 'true'}],
  #           'urls': [{'value': 'http://foo.com/', 'type': 'home'}],
  #           }, {
  #           'id': '123',
  #           'displayName': 'Ms. Bar',
  #           'name': {'formatted': 'Ms. Bar'},
  #           'accounts': [{'domain': 'twitter.com', 'userid': '456'}],
  #           }],
  #       },
  #     self.handler.get_contacts(username='username'))


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
