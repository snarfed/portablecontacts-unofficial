#!/usr/bin/python
"""Twitter source class.

snarfed_org user id: 139199211

Python code to pretty-print JSON response from Twitter REST API:

import json, urllib
pprint(json.loads(urllib.urlopen(
  'https://api.twitter.com/1/users/lookup.json?screen_name=snarfed_org').read()))

import json, urllib
pprint(json.loads(urllib.urlopen(
  'https://api.twitter.com/1/followers/ids.json?screen_name=snarfed_org').read()))
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

import collections
import datetime
import json
import logging
import re

import source

API_FRIENDS_URL = 'https://api.twitter.com/1/friends/ids.json?user_id=%d'
API_USERS_URL = 'https://api.twitter.com/1/users/lookup.json?user_id=%s'
API_ACCOUNT_URL = 'https://api.twitter.com/1/account/verify_credentials.json'


class Twitter(source.Source):
  """Implements the PortableContacts API for Twitter.
  """

  DOMAIN = 'twitter.com'

  def get_contacts(self, user_id=None):
    """Returns a (Python) list of PoCo contacts to be JSON-encoded.

    The OAuth 'Authentication' header must be provided if the current user is
    protected, or to receive any protected friends in the returned contacts.

    Args:
      user_id: integer or string. if provided, only this user will be returned.
    """
    # TODO: handle cursors and repeat to get all users
    if user_id is not None:
      ids = [user_id]
    else:
      resp = self.urlfetch(API_FRIENDS_URL % self.get_current_user())
      ids = json.loads(resp)['ids']

    if not ids:
      return []

    ids_str = ','.join(str(id) for id in ids)
    resp = self.urlfetch(API_USERS_URL % ids_str)
    return [self.to_poco(user) for user in json.loads(resp)]

  def get_current_user(self):
    """Returns the currently authenticated user's id.
    """
    resp = self.urlfetch(API_ACCOUNT_URL)
    return json.loads(resp)['id']

  def urlfetch(self, *args, **kwargs):
    """Wraps Source.urlfetch() and passes through the Authentication header.
    """
    if 'Authentication' in self.handler.request.headers:
      kwargs['headers'] = {'Authentication':
                             self.handler.request.headers['Authentication']}
    return super(Twitter, self).urlfetch(*args, **kwargs)

  def to_poco(self, tw):
    """Converts a Twitter user to a PoCo contact.

    Args:
      tw: dict, a decoded JSON Twitter user
    """
    pc = collections.defaultdict(dict)
    pc['accounts'] = [{'domain': self.DOMAIN}]

    # tw should always have 'id'
    if 'id' in tw:
      pc['id'] = str(tw['id'])
      pc['accounts'][0]['userid'] = str(tw['id'])

    if 'screen_name' in tw:
      pc['accounts'][0]['username'] = tw['screen_name']

    # tw should always have 'name'
    if 'name' in tw:
      pc['displayName'] = tw['name']
      pc['name']['formatted'] = tw['name']

    if 'created_at' in tw:
      # created_at is formatted like 'Sun, 01 Jan 11:44:57 +0000 2012'.
      # remove the time zone, then parse the string, then reformat as ISO 8601.
      created_at = re.sub(' [+-][0-9]{4} ', ' ', tw['created_at'])
      created_at = datetime.datetime.strptime(created_at, '%a %b %d %H:%M:%S %Y')
      pc['published'] = created_at.isoformat()

    if 'profile_image_url' in tw:
      pc['photos'] = [{'value': tw['profile_image_url'], 'primary': 'true'}]

    if 'url' in tw:
      pc['urls'] = [{'value': tw['url'], 'type': 'home'}]

    if 'location' in tw:
      pc['addresses'] = [{
          'formatted': tw['location'],
          'type': 'home',
          }]

    if 'time_zone' in tw:
      # twitter's utc_offset field is seconds, oddly, not hours.
      pc['utcOffset'] =  '%+03d:00' % (tw['utc_offset'] / 60 / 60)

      # also note that twitter's time_zone field provides the user's
      # human-readable time zone, e.g. 'Pacific Time (US & Canada)'. i'd need to
      # include tzdb to parse that, though, and i don't need to since utc_offset
      # works fine.

    if 'description' in tw:
      pc['note'] = tw['description']

    return dict(pc)