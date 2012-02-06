#!/usr/bin/python
"""Facebook handler and schema mapping code.

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
import pprint
import urllib
import urlparse

import appengine_config

from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

ACCOUNT_DOMAIN = 'facebook.com'

class PocoHandler(webapp.RequestHandler):
  """Implements the PortableContacts API for Facebook.
  """
  pass


# schema mapping
# TODO: follow redirects to get pictures
def to_poco(fb):
  pc = collections.defaultdict(dict)

  # facebook friend relationships are always bidirectional
  pc['connected'] = True
  pc['relationships'] = ['friend']


  # fb should always have 'id'
  if 'id' in fb:
    pc['id'] = fb['id']
    pc['accounts'] = [{'domain': ACCOUNT_DOMAIN, 'userid': fb['id']}]

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
    pc['birthday'] = (datetime.datetime.strptime(fb['birthday'], '%m/%d/%Y')
                        .strftime('%Y-%m-%d'))
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
      org['startDate'] = min(p['start_date'] for p in projects)
      org['endDate'] = max(p['end_date'] for p in projects)

  for school in fb.get('education', []):
    org = {}
    pc.setdefault('organizations', []).append(org)
    if 'school' in school:
      org['name'] = school['school'].get('name')
    org['type'] = 'school'
    if 'year' in school:
      org['endDate'] = school['year']

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

  return dict(pc)


application = webapp.WSGIApplication([
    ], debug=appengine_config.DEBUG)

def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
