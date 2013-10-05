#!/usr/bin/python
"""Twitter source class.

Uses the REST API: https://dev.twitter.com/docs/api

TODO: port to
http://code.google.com/p/oauth/source/browse/#svn%2Fcode%2Fpython . tweepy is
just a wrapper around that anyway.
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

import collections
import datetime
import json
import logging
import re
import urllib2
import urlparse

import appengine_config
import source
import tweepy
from webutil import util

API_FRIENDS_URL = 'https://api.twitter.com/1.1/friends/ids.json?user_id=%d'
API_USERS_URL = 'https://api.twitter.com/1.1/users/lookup.json?user_id=%s'
API_ACCOUNT_URL = 'https://api.twitter.com/1.1/account/verify_credentials.json'


class Twitter(source.Source):
  """Implements the PortableContacts API for Twitter.
  """

  DOMAIN = 'twitter.com'
  ITEMS_PER_PAGE = 100
  FRONT_PAGE_TEMPLATE = 'templates/twitter_index.html'
  AUTH_URL = '/start_auth'

  def __init__(self, access_token_key, access_token_secret):
    """Constructor.

    Twitter now requires authentication in v1.1 of their API. You can get an
    OAuth access token by creating an app here: https://dev.twitter.com/apps/new

    Args:
      access_token_key: string, OAuth access token key
      access_token_secret: string, OAuth access token secret
    """
    self.access_token_key = access_token_key
    self.access_token_secret = access_token_secret

  def get_contacts(self, user_id=None, start_index=0, count=0):
    """Returns a (Python) list of PoCo contacts to be JSON-encoded.

    Args:
      user_id: integer or string. if provided, only this user will be returned.
      start_index: int >= 0
      count: int >= 0
    """
    if user_id is not None:
      ids = [user_id]
      total_count = 1
    else:
      cur_user = json.loads(self.urlread(API_ACCOUNT_URL))
      total_count = cur_user.get('friends_count')
      resp = self.urlread(API_FRIENDS_URL % cur_user['id'])
      # TODO: unify with Facebook.get_contacts()
      if count == 0:
        end = self.ITEMS_PER_PAGE - start_index
      else:
        end = start_index + min(count, self.ITEMS_PER_PAGE)
      ids = json.loads(resp)['ids'][start_index:end]

    if not ids:
      return 0, []

    ids_str = ','.join(str(id) for id in ids)
    resp = json.loads(self.urlread(API_USERS_URL % ids_str))

    if user_id is not None and len(resp) == 0:
      # the specified user id doesn't exist
      total_count = 0

    return total_count, [self.to_poco(user) for user in resp]

  def get_current_user(self):
    """Returns the currently authenticated user's id.
    """
    resp = self.urlread(API_ACCOUNT_URL)
    return json.loads(resp)['id']

  def urlread(self, url):
    """Wraps urllib2.urlopen() and adds an OAuth signature.

    TODO: unit test this
    """
    auth = tweepy.OAuthHandler(appengine_config.TWITTER_APP_KEY,
                               appengine_config.TWITTER_APP_SECRET)
    # make sure token key and secret aren't unicode because python's hmac
    # module (used by tweepy/oauth.py) expects strings.
    # http://stackoverflow.com/questions/11396789
    auth.set_access_token(str(self.access_token_key),
                          str(self.access_token_secret))

    parsed = urlparse.urlparse(url)
    url_without_query = urlparse.urlunparse(list(parsed[0:4]) + ['', ''])
    headers = {}
    auth.apply_auth(url_without_query, 'GET', headers,
                    dict(urlparse.parse_qsl(parsed.query)))
    logging.info('Populated Authorization header from access token: %s',
                 headers.get('Authorization'))

    return urllib2.urlopen(urllib2.Request(url, headers=headers)).read()

  def to_poco(self, tw):
    """Converts a Twitter user to a PoCo contact.

    Args:
      tw: dict, a decoded JSON Twitter user
    """
    pc = collections.defaultdict(dict)
    pc['accounts'] = [{'domain': self.DOMAIN}]

    # tw should always have 'id' (it's an int)
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

    utc_offset = tw.get('utc_offset')
    if utc_offset is not None:
      # twitter's utc_offset field is seconds, oddly, not hours.
      pc['utcOffset'] =  '%+03d:00' % (tw['utc_offset'] / 60 / 60)

      # also note that twitter's time_zone field provides the user's
      # human-readable time zone, e.g. 'Pacific Time (US & Canada)'. i'd need to
      # include tzdb to parse that, though, and i don't need to since utc_offset
      # works fine.

    if 'description' in tw:
      pc['note'] = tw['description']

    return dict(pc)
