#!/usr/bin/python
"""Unit tests for facebook.py.
"""

__author__ = ['Ryan Barrett <portablecontacts-unofficial@ryanb.org>']

import datetime
import json
import logging
import mox
import unittest
import urllib
import urlparse

import facebook
import testutil

from google.appengine.ext import webapp


class FacebookTest(testutil.HandlerTest):

  def test_to_poco_id_only(self):
    self.assert_equals(
        {'id': '212038'},
        facebook.to_poco({'id': '212038'}))

  def test_to_poco_minimal(self):
    self.assert_equals({
          'id': '212038',
          'displayName': 'Ryan Barrett',
          'name': {'formatted': 'Ryan Barrett'},
          },
      facebook.to_poco({
          'id': '212038',
          'name': 'Ryan Barrett',
         }))

  def test_to_poco_full(self):
    self.assert_equals({
        'id': '212038',
        'displayName': 'Ryan Barrett',
        'name': {'formatted': 'Ryan Barrett',
                 'givenName': 'Ryan',
                 'familyName': 'Barrett'},
        'birthday': '1980-10-01',
        'gender': 'male',
        'emails': [{'value': 'ryan@example.com',
                    'type': 'home',
                    'primary': 'true',
                    }],
        'urls': [{'value': 'http://snarfed.org/',
                  'type': 'home',
                  }],
        # 'photos': [{'value': 'http://sample.site.org/photos/12345.jpg',
        #             'type': 'thumbnail'
        #             }],
      # 'ims': [
      #   {
      #     'value': 'plaxodev8',
      #     'type': 'aim'
      #   }
      # ],
      # 'addresses': [
      #   {
      #     'type': 'home',
      #     'streetAddress': '742 Evergreen Terrace\nSuite 123',
      #     'locality': 'Springfield',

      #     'region': 'VT',
      #     'postalCode': '12345',
      #     'country': 'USA',
      #     'formatted': '742 Evergreen Terrace\nSuite 123\nSpringfield, VT 12345 USA'
      #   }
      # ],
      'organizations': [
          {'name': 'Google', 'type': 'job', 'title': 'Software Engineer',
           'startDate': '2002-01', 'endDate': '2010-01'},
          {'name': 'IBM', 'type': 'job'},
          {'name': 'Polytechnic', 'type': 'school'},
          {'name': 'Stanford', 'type': 'school', 'endDate': '2002'},
          ],
      # 'accounts': [
      #   {
      #     'domain': 'plaxo.com',
      #     'userid': '2706'
      #   }
      # ]
        },
      facebook.to_poco({
          'id': '212038',
          'name': 'Ryan Barrett',
          'first_name': 'Ryan',
          'last_name': 'Barrett',
          'link': 'http://www.facebook.com/snarfed.org',
          'username': 'snarfed.org',
          'birthday': '10/01/1980',
           # 'location': {
           #   'id': '114952118516947',
           #   'name': 'San Francisco, California'
           # },
           'work': [{
              'employer': {'id': '104958162837', 'name': 'Google'},
              'projects': [{
                  'id': '399089423614',
                  'name': 'App Engine',
                  'start_date': '2005-01',
                  'end_date': '2010-01'
                  }, {
                  'id': '100680586640141',
                  'name': 'Moneta',
                  'start_date': '2002-01',
                  'end_date': '2006-01',
                  }],
              'position': 'Software Engineer',
              }, {
              'employer': {'name': 'IBM'},
              }],
           'education': [{
              'school': {'id': '7590844925','name': 'Polytechnic'},
              'type': 'High School'
              }, {
              'school': {'id': '6192688417', 'name': 'Stanford'},
              'year': '2002',
              'type': 'Graduate School'
              }],
           'gender': 'male',
           'email': 'ryan@example.com',
           'website': 'http://snarfed.org/',
           # 'timezone': -8,
           # 'locale': 'en_US',
           # 'verified': true,
           # 'updated_time': '2012-01-06T02:11:04+0000',
           # 'type': 'user'
                   }))
