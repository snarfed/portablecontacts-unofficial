#!/usr/bin/python
"""Unit tests for facebook.py.
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

import datetime
import json
import unittest

import facebook
import testutil

from google.appengine.ext import webapp


class FacebookTest(testutil.HandlerTest):

  def test_to_poco_id_only(self):
    self.assert_equals(
        {'id': '212038',
         'accounts': [{'domain': 'facebook.com', 'userid': '212038'}],
         },
        facebook.to_poco({'id': '212038'}))

  def test_to_poco_minimal(self):
    self.assert_equals({
        'id': '212038',
        'displayName': 'Ryan Barrett',
        'name': {'formatted': 'Ryan Barrett'},
        'accounts': [{'domain': 'facebook.com', 'userid': '212038'}],
        'addresses': [{'formatted': 'San Francisco, California',
                       'type': 'home',
                       }],
        },
      facebook.to_poco({
        'id': '212038',
        'name': 'Ryan Barrett',
        'location': {'id': '123', 'name': 'San Francisco, California'},
        }))

  def test_to_poco_full(self):
    self.assert_equals({
        'id': '212038',
        'displayName': 'Ryan Barrett',
        'name': {'formatted': 'Ryan Barrett',
                 'givenName': 'Ryan',
                 'familyName': 'Barrett',
                 },
        'accounts': [{'domain': 'facebook.com',
                      'userid': '212038',
                      'username': 'snarfed.org',
                      }],
        'birthday': '1980-10-01',
        'addresses': [{
          'streetAddress': '1 Palm Dr.',
          'locality': 'Palo Alto',
          'region': 'California',
          'postalCode': '94301',
          'country': 'United States',
          'type': 'home',
          }],
        'phoneNumbers': [{'value': '1234567890', 'type': 'mobile'}],
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
        'organizations': [
          {'name': 'Google', 'type': 'job', 'title': 'Software Engineer',
           'startDate': '2002-01', 'endDate': '2010-01'},
          {'name': 'IBM', 'type': 'job'},
          {'name': 'Polytechnic', 'type': 'school'},
          {'name': 'Stanford', 'type': 'school', 'endDate': '2002'},
          ],
        },
      facebook.to_poco({
          'id': '212038',
          'name': 'Ryan Barrett',
          'first_name': 'Ryan',
          'last_name': 'Barrett',
          'link': 'http://www.facebook.com/snarfed.org',
          'username': 'snarfed.org',
          'birthday': '10/01/1980',
          'location': {
            'id': '123',
            'name': 'San Francisco, California'
            },
          'address': {
            'street': '1 Palm Dr.',
            'city': 'Palo Alto',
            'state': 'California',
            'country': 'United States',
            'zip': '94301',
            },
          'mobile_phone': '1234567890',
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
          }))
