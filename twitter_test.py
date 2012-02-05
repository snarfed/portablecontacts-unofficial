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
        'addresses': [{'formatted': 'San Francisco, CA',
                       'type': 'home',
                       }],
        },
      twitter.to_poco({
        'id': 139199211,
        'name': 'Ryan Barrett',
        'location': 'San Francisco, CA',
        }))

  def test_to_poco_full(self):
    self.assert_equals({
        'id': '139199211',
        'displayName': 'Ryan Barrett',
        'name': {'formatted': 'Ryan Barrett',
      #            'givenName': 'Ryan',
      #            'familyName': 'Barrett',
        },
        'accounts': [{'domain': 'twitter.com',
                      'userid': '139199211',
                      'username': 'snarfed_org',
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
      #   'urls': [{'value': 'http://snarfed.org/',
      #             'type': 'home',
      #             }],
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
        },
      twitter.to_poco({
            # 'contributors_enabled': False,
            # 'created_at': 'Sat May 01 21:42:43 +0000 2010',
            # 'default_profile': True,
            # 'default_profile_image': False,
            # 'description': '',
            # 'favourites_count': 0,
            # 'follow_request_sent': None,
            # 'followers_count': 75,
            # 'following': None,
            # 'friends_count': 80,
            # 'geo_enabled': False,
            'id': 139199211,
            'id_str': '139199211',
            # 'is_translator': False,
            # 'lang': 'en',
            # 'listed_count': 1,
            # 'location': 'San Francisco',
            'name': 'Ryan Barrett',
            # 'notifications': None,
            # 'profile_background_color': 'C0DEED',
            # 'profile_background_image_url': 'http://a0.twimg.com/images/themes/theme1/bg.png',
            # 'profile_background_image_url_https': 'https://si0.twimg.com/images/themes/theme1/bg.png',
            # 'profile_background_tile': False,
            # 'profile_image_url': 'http://a1.twimg.com/profile_images/866165047/ryan_normal.jpg',
            # 'profile_image_url_https': 'https://si0.twimg.com/profile_images/866165047/ryan_normal.jpg',
            # 'profile_link_color': '0084B4',
            # 'profile_sidebar_border_color': 'C0DEED',
            # 'profile_sidebar_fill_color': 'DDEEF6',
            # 'profile_text_color': '333333',
            # 'profile_use_background_image': True,
            # 'protected': False,
            'screen_name': 'snarfed_org',
            # 'show_all_inline_media': False,
            # # 'status': {'contributors': None,
            # #            'coordinates': None,
            # #            'created_at': 'Wed Feb 01 23:43:39 +0000 2012',
            # #            'favorited': False,
            # #            'geo': None,
            # #            'id': 164856466455527426,
            # #            'id_str': '164856466455527426',
            # #            'in_reply_to_screen_name': 'cynk',
            # #            'in_reply_to_status_id': 164834409340616705,
            # #            'in_reply_to_status_id_str': '164834409340616705',
            # #            'in_reply_to_user_id': 1321791,
            # #            'in_reply_to_user_id_str': '1321791',
            # #            'place': None,
            # #            'retweet_count': 0,
            # #            'retweeted': False,
            # #            'source': 'web',
            # #            'text': '@cynk when was it a good thing? :P',
            # #            'ytruncated': False},
            # 'statuses_count': 104,
            # 'time_zone': 'Pacific Time (US & Canada)',
            # 'url': 'http://snarfed.org/',
            # 'utc_offset': -28800,
            # 'verified': False,
            }))

    # [
    #   {
    #     "name": "Twitter API",
    #     "profile_sidebar_border_color": "87bc44",
    #     "profile_background_tile": false,
    #     "profile_sidebar_fill_color": "e0ff92",
    #     "location": "San Francisco, CA",
    #     "profile_image_url": "http://a3.twimg.com/profile_images/689684365/api_normal.png",
    #     "created_at": "Wed May 23 06:01:13 +0000 2007",
    #     "profile_link_color": "0000ff",
    #     "favourites_count": 2,
    #     "url": "http://apiwiki.twitter.com",
    #     "contributors_enabled": true,
    #     "utc_offset": -28800,
    #     "id": 6253282,
    #     "profile_use_background_image": true,
    #     "profile_text_color": "000000",
    #     "protected": false,
    #     "followers_count": 160752,
    #     "lang": "en",
    #     "verified": true,
    #     "profile_background_color": "c1dfee",
    #     "geo_enabled": true,
    #     "notifications": false,
    #     "description": "The Real Twitter API. I tweet about API changes, service issues and happily answer questions about Twitter and our API. Don't get an answer? It's on my website.",
    #     "time_zone": "Pacific Time (US & Canada)",
    #     "friends_count": 19,
    #     "statuses_count": 1858,
    #     "profile_background_image_url": "http://a3.twimg.com/profile_background_images/59931895/twitterapi-background-new.png",
    #     "status": {
    #       "coordinates": null,
    #       "favorited": false,
    #       "created_at": "Tue Jun 22 16:53:28 +0000 2010",
    #       "truncated": false,
    #       "text": "@Demonicpagan possible some part of your signature generation is incorrect & fails for real reasons.. follow up on the list if you suspect",
    #       "contributors": null,
    #       "id": 16783999399,
    #       "geo": null,
    #       "in_reply_to_user_id": 6339722,
    #       "place": null,
    #       "source": "<a href="http://www.tweetdeck.com" rel="nofollow">TweetDeck</a>",
    #       "in_reply_to_screen_name": "Demonicpagan",
    #       "in_reply_to_status_id": 16781827477
    #     },
    #     "screen_name": "twitterapi",
    #     "following": false
    #   },
    #   {
    #     "name": "Twitter",
    #     "profile_sidebar_border_color": "EEEEEE",
    #     "profile_background_tile": false,
    #     "profile_sidebar_fill_color": "F6F6F6",
    #     "location": "San Francisco, CA",
    #     "profile_image_url": "http://a1.twimg.com/profile_images/878669694/twitter_bird_normal.jpg",
    #     "created_at": "Tue Feb 20 14:35:54 +0000 2007",
    #     "profile_link_color": "038543",
    #     "favourites_count": 2,
    #     "url": "http://twitter.com",
    #     "contributors_enabled": true,
    #     "utc_offset": -28800,
    #     "id": 783214,
    #     "profile_use_background_image": true,
    #     "profile_text_color": "333333",
    #     "protected": false,
    #     "followers_count": 3305606,
    #     "lang": "en",
    #     "verified": true,
    #     "profile_background_color": "ACDED6",
    #     "geo_enabled": true,
    #     "notifications": false,
    #     "description": "Always wondering what's happening. ",
    #     "time_zone": "Pacific Time (US & Canada)",
    #     "friends_count": 257,
    #     "statuses_count": 774,
    #     "profile_background_image_url": "http://s.twimg.com/a/1276896641/images/themes/theme18/bg.gif",
    #     "status": {
    #       "coordinates": null,
    #       "favorited": false,
    #       "created_at": "Tue Jun 22 16:40:19 +0000 2010",
    #       "truncated": false,
    #       "text": "9 cool things to do with your Twitter account (via @pastemagazine) http://bit.ly/c0LdC6",
    #       "contributors": [
    #         16739704
    #       ],
    #       "id": 16783169544,
    #       "geo": null,
    #       "in_reply_to_user_id": null,
    #       "place": null,
    #       "source": "web",
    #       "in_reply_to_screen_name": null,
    #       "in_reply_to_status_id": null
    #     },
    #     "screen_name": "twitter",
    #     "following": false
    #   }
    # ]
