"""Facebook source class.

NOTE:
eventually fb will turn phone and address back on. when they do, add scopes:
user_mobile_phone, user_address to get them. (same with IM addresses, but i
couldn't find anywhere they talk about that at all.)

background:
https://developers.facebook.com/blog/post/447/
https://developers.facebook.com/blog/post/446/
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

import collections
import datetime
import json
import logging
import re
import urllib
import urllib2
import urlparse

import appengine_config
import source

OAUTH_SCOPES = ','.join((
    'email',
    'user_about_me',
    'user_birthday',
    'user_education_history',
    'user_location',
    'user_notes',
    'user_website',
    'user_work_history',
    # see comment in file docstring
    # 'user_address',
    # 'user_mobile_phone',
    ))

API_URL = 'https://graph.facebook.com/'
API_USER_URL = 'https://graph.facebook.com/%s'

# a single batch graph API request that returns all details for the current
# user's friends. the first embedded request gets the current user's list of
# friends; the second gets their details, using JSONPath syntax to depend on the
# first.
#
# copied from
# https://developers.facebook.com/docs/reference/api/batch/#operations
#
# also note that the docs only discuss including the access token inside the
# batch JSON value, but including it in the query parameter of the POST URL
# works fine too.
# See "Specifying different access tokens for different operations" in
# https://developers.facebook.com/docs/reference/api/batch/#operations
API_FRIENDS_BATCH_REQUESTS = json.dumps([
    {'method': 'GET', 'name': 'friends', 'relative_url':
       'me/friends?offset=%(offset)d&limit=%(limit)d'},
    {'method': 'GET', 'relative_url': '?ids={result=friends:$.data.*.id}'},
    ])


class Facebook(source.Source):
  """Implements the PortableContacts API for Facebook.
  """

  DOMAIN = 'facebook.com'
  FRONT_PAGE_TEMPLATE = 'templates/facebook_index.html'
  AUTH_URL = '/start_auth'

  def __init__(self, access_token=None):
    """Constructor.

    If an OAuth access token is provided, it will be passed on to Facebook. This
    will be necessary for some people and contact details, based on their
    privacy settings.

    Args:
      access_token: string, optional OAuth access token
    """
    self.access_token = access_token

  def get_contacts(self, user_id=None, start_index=0, count=0):
    """Returns a (Python) list of PoCo contacts to be JSON-encoded.

    Args:
      user_id: integer or string. if provided, only this user will be returned.
      start_index: int >= 0
      count: int >= 0
    """
    if user_id is not None:
      resp = self.urlread(API_USER_URL % user_id)
      friends = [json.loads(resp)]
    else:
      batch = urllib.urlencode({'batch': API_FRIENDS_BATCH_REQUESTS %
                                {'offset': start_index, 'limit': count}})
      resp = self.urlread(API_URL, data=batch)
      # the batch response is a list of responses to the individual batch
      # requests, e.g.
      #
      # [null, {'body': "{'1': {...}, '2': {...}}"}]
      #
      # details: https://developers.facebook.com/docs/reference/api/batch/
      #
      # the first response will be null since the second depends on it
      # and facebook omits responses to dependency requests.
      friends = json.loads(json.loads(resp)[1]['body']).values()

    # return None for total_count since we'd have to fetch and count all
    # friends, which doesn't scale.
    return None, [self.to_poco(user) for user in friends]

  def get_current_user(self):
    """Returns 'me', which Facebook interprets as the current user.
    """
    return 'me'

  def urlread(self, url, **kwargs):
    """Wraps urllib2.urlopen() and passes through the access token.

    Keyword args are passed through to urllib2.Request.
    """
    if self.access_token:
      parsed = list(urlparse.urlparse(url))
      # query params are in index 4
      params = urlparse.parse_qsl(parsed[4]) + [('access_token', self.access_token)]
      parsed[4] = urllib.urlencode(params)
      url = urlparse.urlunparse(parsed)

    logging.info('Fetching %s with %s', url, kwargs)
    return urllib2.urlopen(urllib2.Request(url, **kwargs)).read()

  def to_poco(self, fb):
    """Converts a Facebook user to a PoCo contact.

    Args:
      fb: dict, a decoded JSON Facebook user
    """
    pc = collections.defaultdict(dict)

    # facebook friend relationships are always bidirectional
    # TODO: remove this (or replace with something like "self"?) for the current
    # user's contact
    pc['connected'] = True
    pc['relationships'] = ['friend']

    pc['accounts'] = [{'domain': self.DOMAIN}]

    # fb should always have 'id'
    if 'id' in fb:
      pc['id'] = fb['id']
      pc['accounts'][0]['userid'] = fb['id']

    if 'username' in fb:
      pc['accounts'][0]['username'] = fb['username']

    # fb should always have 'name'
    if 'name' in fb:
      pc['displayName'] = fb['name']
      pc['name']['formatted'] = fb['name']

    if 'first_name' in fb:
      pc['name']['givenName'] = fb['first_name']

    if 'last_name' in fb:
      pc['name']['familyName'] = fb['last_name']

    if 'birthday' in fb:
      match = re.match(r'(\d{1,2})/(\d{1,2})/?(\d{4})?', fb['birthday'])
      month, day, year = match.groups()
      if not year:
        year = '0000'
      pc['birthday'] = '%s-%02d-%02d' % (year, int(month), int(day))

    if 'gender' in fb:
      pc['gender'] = fb['gender']

    if 'email' in fb:
      pc['emails'] = [{'value': fb['email'], 'type': 'home', 'primary': 'true'}]

    if 'website' in fb:
      pc['urls'] = [{'value': fb['website'], 'type': 'home'}]

    for work in fb.get('work', []):
      org = {}
      pc.setdefault('organizations', []).append(org)
      if 'employer' in work:
        org['name'] = work['employer'].get('name')
      org['type'] = 'job'
      if 'position' in work:
        org['title'] = work['position']

      projects = work.get('projects')
      if 'projects' in work:
        # TODO: convert these to proper xs:date (ISO 8601) format, e.g.
        # 2008-01-23T04:56:22Z
        org['startDate'] = min(p.get('start_date') for p in projects)
        org['endDate'] = max(p.get('end_date') for p in projects)

    for school in fb.get('education', []):
      org = {}
      pc.setdefault('organizations', []).append(org)
      if 'school' in school:
        org['name'] = school['school'].get('name')
      org['type'] = 'school'

      year = school.get('year')
      if isinstance(year, dict):
        org['endDate'] = year.get('name')
      elif isinstance(year, basestring):
        org['endDate'] = year

    if 'address' in fb:
      addr = fb['address']
      pc['addresses'] = [{
          'streetAddress': addr['street'],
          'locality': addr['city'],
          'region': addr['state'],
          'country': addr['country'],
          'postalCode': addr['zip'],
          'type': 'home',
          }]
    elif 'location' in fb:
      pc['addresses'] = [{
          'formatted': fb['location'].get('name'),
          'type': 'home',
          }]

    if 'mobile_phone' in fb:
      pc['phoneNumbers'] = [{
          'value': fb['mobile_phone'],
          'type': 'mobile',
          }]

    if 'timezone' in fb:
      pc['utcOffset'] = '%+03d:00' % fb['timezone']

    if 'updated_time' in fb:
      pc['updated'] = fb['updated_time']

    if 'bio' in fb:
      pc['note'] = fb['bio']

    # profile picture. facebook graph api provides a url that 302 redirects and
    # takes either id or username.
    handle = fb.get('id', fb.get('username'))
    if handle:
      url = 'http://graph.facebook.com/%s/picture?type=large' % handle
      pc['photos'] = [{'value': url}]

    return dict(pc)
