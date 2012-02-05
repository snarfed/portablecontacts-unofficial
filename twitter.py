#!/usr/bin/python
"""Twitter handler and schema mapping code.

Python code to pretty-print JSON responses from Twitter Search API:

import json, urllib
pprint.pprint(json.loads(urllib.urlopen(
  'http://search.twitter.com/search.json?q=snarfed.org+filter%3Alinks&include_entities=true&result_type=recent&rpp=100').read()))
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

import collections
import datetime
import json
import logging
import urllib

import appengine_config

from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


ACCOUNT_DOMAIN = 'twitter.com'

class PocoHandler(webapp.RequestHandler):
  """Implements the PortableContacts API for Twitter.
  """
  pass


# schema mapping
# TODO: follow redirects to get pictures
def to_poco(tw):
  pc = collections.defaultdict(dict)
  pc['accounts'] = [{'domain': ACCOUNT_DOMAIN}]

  # this should always be true
  if 'id' in tw:
    pc['id'] = str(tw['id'])
    pc['accounts'][0]['userid'] = str(tw['id'])

  if 'screen_name' in tw:
    pc['accounts'][0]['username'] = tw['screen_name']

  # this should always be true
  if 'name' in tw:
    pc['displayName'] = tw['name']
    pc['name']['formatted'] = tw['name']

  # if 'first_name' in tw:
  #   pc['name']['givenName'] = tw['first_name']

  # if 'last_name' in tw:
  #   pc['name']['familyName'] = tw['last_name']

  # if 'birthday' in tw:
  #   pc['birthday'] = (datetime.datetime.strptime(tw['birthday'], '%m/%d/%Y')
  #                       .strftime('%Y-%m-%d'))
  # if 'gender' in tw:
  #   pc['gender'] = tw['gender']

  # if 'email' in tw:
  #   pc['emails'] = [{'value': tw['email'], 'type': 'home', 'primary': 'true'}]

  # if 'website' in tw:
  #   pc['urls'] = [{'value': tw['website'], 'type': 'home'}]

  # for work in tw.get('work', []):
  #   org = {}
  #   pc.setdefault('organizations', []).append(org)
  #   if 'employer' in work:
  #     org['name'] = work['employer'].get('name')
  #   org['type'] = 'job'
  #   if 'position' in work:
  #     org['title'] = work['position']

  #   projects = work.get('projects')
  #   if 'projects' in work:
  #     # TODO: convert these to proper xs:date (ISO 8601) format, e.g.
  #     # 2008-01-23T04:56:22Z
  #     org['startDate'] = min(p['start_date'] for p in projects)
  #     org['endDate'] = max(p['end_date'] for p in projects)

  # for school in tw.get('education', []):
  #   org = {}
  #   pc.setdefault('organizations', []).append(org)
  #   if 'school' in school:
  #     org['name'] = school['school'].get('name')
  #   org['type'] = 'school'
  #   if 'year' in school:
  #     org['endDate'] = school['year']

  if 'location' in tw:
    pc['addresses'] = [{
        'formatted': tw['location'],
        'type': 'home',
        }]

  # if 'mobile_phone' in tw:
  #   pc['phoneNumbers'] = [{
  #       'value': tw['mobile_phone'],
  #       'type': 'mobile',
  #       }]

  return dict(pc)


application = webapp.WSGIApplication([
    ], debug=appengine_config.DEBUG)

def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
