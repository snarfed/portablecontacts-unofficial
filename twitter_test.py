#!/usr/bin/python
"""Unit tests for twitter.py.
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

import datetime
import json
import unittest

from webob import exc

import testutil
import twitter

from google.appengine.ext import webapp


class TwitterTest(testutil.HandlerTest):

  def setUp(self):
    super(TwitterTest, self).setUp()
    self.handler = twitter.Handler()
    self.handler.initialize(self.request, self.response)

  def test_get_contacts(self):
    self.expect_urlfetch(
      'https://api.twitter.com/1/account/verify_credentials.json',
      '{"id": 9}')
    self.expect_urlfetch(
      'https://api.twitter.com/1/friends/ids.json?user_id=9',
      '{"ids": [123, 456]}')
    self.expect_urlfetch(
      'https://api.twitter.com/1/users/lookup.json?user_id=123,456',
      json.dumps([{
          'id': 123,
          'screen_name': 'foo',
          'name': 'Mr. Foo',
          'location': 'Hometown',
          'url': 'http://foo.com/',
          'profile_image_url': 'http://foo.com/pic.jpg',
          }, {
          'id': 456,
          'name': 'Ms. Bar',
          }]))
    self.mox.ReplayAll()

    self.assert_equals([{
          'id': '123',
          'displayName': 'Mr. Foo',
          'name': {'formatted': 'Mr. Foo'},
          'accounts': [{'domain': 'twitter.com',
                        'userid': '123',
                        'username': 'foo'}],
          'addresses': [{'formatted': 'Hometown', 'type': 'home'}],
          'photos': [{'value': 'http://foo.com/pic.jpg', 'primary': 'true'}],
          'urls': [{'value': 'http://foo.com/', 'type': 'home'}],
          }, {
          'id': '456',
          'displayName': 'Ms. Bar',
          'name': {'formatted': 'Ms. Bar'},
          'accounts': [{'domain': 'twitter.com', 'userid': '456'}],
          }],
      self.handler.get_contacts())

  def test_get_contacts_user_id(self):
    self.expect_urlfetch(
      'https://api.twitter.com/1/users/lookup.json?user_id=123',
      '[]')
    self.mox.ReplayAll()
    self.assert_equals([], self.handler.get_contacts(user_id=123))

  def test_get_contacts_passes_through_auth_header(self):
    self.expect_urlfetch(
      'https://api.twitter.com/1/account/verify_credentials.json',
      '{"id": 9}',
      headers={'Authentication': 'insert oauth here'})
    self.expect_urlfetch(
      'https://api.twitter.com/1/friends/ids.json?user_id=9',
      '{"ids": []}',
      headers={'Authentication': 'insert oauth here'})
    self.mox.ReplayAll()

    self.handler.request.headers['Authentication'] = 'insert oauth here'
    self.assert_equals([], self.handler.get_contacts())

  def test_get_current_user_id(self):
    self.expect_urlfetch(
      'https://api.twitter.com/1/account/verify_credentials.json',
      '{"id": 9}')
    self.mox.ReplayAll()
    self.assert_equals(9, self.handler.get_current_user_id())

  def test_to_poco_id_only(self):
    self.assert_equals(
        {'id': '139199211',
         'accounts': [{'domain': 'twitter.com', 'userid': '139199211'}],
         },
        self.handler.to_poco({'id': 139199211}))

  def test_to_poco_minimal(self):
    self.assert_equals({
        'id': '139199211',
        'displayName': 'Ryan Barrett',
        'name': {'formatted': 'Ryan Barrett'},
        'accounts': [{'domain': 'twitter.com', 'userid': '139199211'}],
        },
      self.handler.to_poco({
        'id': 139199211,
        'name': 'Ryan Barrett',
        }))

  def test_to_poco_full(self):
    self.assert_equals({
        'id': '139199211',
        'displayName': 'Ryan Barrett',
        'name': {'formatted': 'Ryan Barrett'},
        'accounts': [{'domain': 'twitter.com',
                      'userid': '139199211',
                      'username': 'snarfed_org',
                      }],
        'addresses': [{'formatted': 'San Francisco, CA',
                       'type': 'home',
                       }],
        'published': '2007-05-23T06:01:13',
        'photos': [{'value': 'http://a1.twimg.com/profile_images/866165047/ryan_normal.jpg',
                    'primary': 'true',
                    }],
        'urls': [{'value': 'http://snarfed.org/',
                  'type': 'home',
                  }],
        'utcOffset': '-08:00',
        'note': 'something about me',
        },
      self.handler.to_poco({
          'description': 'something about me',
          'id': 139199211,
          'id_str': '139199211',
          'location': 'San Francisco, CA',
          'name': 'Ryan Barrett',
          'profile_image_url': 'http://a1.twimg.com/profile_images/866165047/ryan_normal.jpg',
          'screen_name': 'snarfed_org',
          'created_at': 'Wed May 23 06:01:13 +0000 2007',
          'time_zone': 'Pacific Time (US & Canada)',
          'url': 'http://snarfed.org/',
          'utc_offset': -28800,
          }))
