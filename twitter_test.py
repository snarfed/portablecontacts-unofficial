#!/usr/bin/python
"""Unit tests for twitter.py.
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

import datetime
import json
import unittest

import testutil
import twitter

from google.appengine.ext import webapp


class TwitterTest(testutil.HandlerTest):

  def test_to_poco_id_only(self):
    self.assert_equals(
        {'id': '139199211',
         'accounts': [{'domain': 'twitter.com', 'userid': '139199211'}],
         },
        twitter.to_poco({'id': 139199211}))

  def test_to_poco_minimal(self):
    self.assert_equals({
        'id': '139199211',
        'displayName': 'Ryan Barrett',
        'name': {'formatted': 'Ryan Barrett'},
        'accounts': [{'domain': 'twitter.com', 'userid': '139199211'}],
        },
      twitter.to_poco({
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
      #   'birthday': '1980-10-01',
      #   'addresses': [{
      #     'streetAddress': '1 Palm Dr.',
      #     'locality': 'Palo Alto',
      #     'region': 'California',
      #     'postalCode': '94301',
      #     'country': 'United States',
      #     'type': 'home',
      #     }],
      #   'phoneNumbers': [{'value': '1234567890', 'type': 'mobile'}],
      #   'gender': 'male',
      #   'emails': [{'value': 'ryan@example.com',
      #               'type': 'home',
      #               'primary': 'true',
      #               }],
        'urls': [{'value': 'http://snarfed.org/',
                  'type': 'home',
                  }],
      #   # 'photos': [{'value': 'http://sample.site.org/photos/12345.jpg',
      #   #             'type': 'thumbnail'
      #   #             }],
      # # 'ims': [
      # #   {
      # #     'value': 'plaxodev8',
      # #     'type': 'aim'
      # #   }
      # # ],
      #   'organizations': [
      #     {'name': 'Google', 'type': 'job', 'title': 'Software Engineer',
      #      'startDate': '2002-01', 'endDate': '2010-01'},
      #     {'name': 'IBM', 'type': 'job'},
      #     {'name': 'Polytechnic', 'type': 'school'},
      #     {'name': 'Stanford', 'type': 'school', 'endDate': '2002'},
      #     ],
        'utcOffset': '-08:00',
        # 'updated': '2012-01-06T02:11:04+0000',
        # 'connected': True,
        # 'relationships': ['friend'],
        'note': 'something about me',
        },
      twitter.to_poco({
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
