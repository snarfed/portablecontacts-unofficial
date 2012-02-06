#!/usr/bin/python
"""Twitter handler and schema mapping code.

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
import urllib

import appengine_config
import poco

from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

ACCOUNT_DOMAIN = 'twitter.com'
API_FOLLOWERS_URL = 'https://api.twitter.com/1/followers/ids.json'
API_USERS_URL = 'https://api.twitter.com/1/users/lookup.json'


class TwitterHandler(poco.PocoHandler):
  """Implements the PortableContacts API for Twitter.
  """

  def get_contacts(self, user_id=None, username=None):
    """Returns a (Python) list of PoCo contacts to be JSON-encoded.

    Twitter doesn't infer the current user from OAuth credentials, so user_id or
    username should be provided. Also, the OAuth 'Authentication' header must
    be provided if the user is protected.
    """
    assert (user_id is not None) ^ (username is not None)  # xor
    if user_id:
      param = '?user_id=%d' % user_id
    else:
      param = '?screen_name=%s' % urllib.quote_plus(username)

    resp = urlfetch.fetch(API_FOLLOWERS_URL + param, deadline=999)
    # TODO: refactor
    if resp.status_code != 200:
      # return the Twitter response to the client
      self.response.set_status(resp.status_code)
      self.response.headers.update(resp.headers)
      self.response.out.write(resp.content)

    # TODO: handle cursors and repeat to get all users
    ids = json.loads(resp.content)['ids']
    if not ids:
      return []

    param = '?user_id=%s' % ','.join(str(id) for id in ids)
    resp = urlfetch.fetch(API_USERS_URL + param, deadline=999)
    if resp.status_code != 200:
      # return the Twitter response to the client
      self.response.set_status(resp.status_code)
      self.response.headers.update(resp.headers)
      self.response.out.write(resp.content)

    return [self.to_poco(user) for user in json.loads(resp.content)]

  def to_poco(self, tw):
    """Converts a Twitter user to a PoCo user.
  
    Args:
      tw: dict, a decoded JSON Twitter user
    """
    pc = collections.defaultdict(dict)
    pc['accounts'] = [{'domain': ACCOUNT_DOMAIN}]
  
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


application = webapp.WSGIApplication([
    ], debug=appengine_config.DEBUG)

def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
