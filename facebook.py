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

__author__ = ['Ryan Barrett <portablecontacts-unofficial@ryanb.org>']

import collections
import datetime
import json
import logging
import pprint
import urllib
import urlparse

import appengine_config

from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

ACCOUNT_DOMAIN = 'facebook.com'
OAUTH_SCOPES = ','.join((
    'friends_about_me',
    'friends_birthday',
    'friends_education_history',
    'friends_hometown',
    'friends_location',
    'friends_work_history',
    ))

# facebook oauth url templates for client side flow. can't (easily) use
# urllib.urlencode() because i want to keep the %(...)s placeholders as is and
# fill them in later in code.
GET_AUTH_CODE_URL = '&'.join((
    ('http://localhost:8000/dialog/oauth/?'
     if appengine_config.MOCKFACEBOOK else
     'https://www.facebook.com/dialog/oauth/?'),
    'scope=%s' % OAUTH_SCOPES,
    'client_id=%(client_id)s',
    # redirect_uri here must be the same in the access token request!
    'redirect_uri=%(host_url)s/facebook/got_auth_code',
    'response_type=token',
    'state=%(state)s',
    ))


class FacebookApp(webapp.RequestHandler):
  """Interacts with Facebook's OAuth and Graph APIs.
  """

  @classmethod
  def get_access_token(self):
    """Gets an access token for the current user.

    Redirects to the current request URL.
    """
    url = GET_ACCESS_TOKEN_URL % {
      'auth_code': auth_code,
      'client_id': appengine_config.FACEBOOK_APP_ID,
      'client_secret': appengine_config.FACEBOOK_APP_SECRET,
      'host_url': handler.request.host_url,
      }
    resp = urlfetch.fetch(url, deadline=999)
    # TODO: error handling. handle permission declines, errors, etc
    logging.debug('access token response: %s' % resp.content)
    params = urlparse.parse_qs(resp.content)
    access_token = params['access_token'][0]

    url = '%s?access_token=%s' % (redirect_uri, access_token)
    handler.redirect(url)


class AddFacebookPage(webapp.RequestHandler):
  def post(self):
    FacebookApp.get().get_access_token(self, '/facebook/got_access_token')


class GotAuthCode(webapp.RequestHandler):
  def get(self):
    FacebookApp.get()._get_access_token_with_auth_code(
      self, self.request.params['code'], self.request.params['state'])


class GotAccessToken(webapp.RequestHandler):
  def get(self):
    FacebookPage.create_new(self)
    self.redirect('/')


class PocoHandler(webapp.RequestHandler):
  """Implements the PortableContacts API for Facebook.
  """
  pass


# schema mapping
# TODO: follow redirects to get pictures
def to_poco(fb):
  pc = collections.defaultdict(dict)
  pc['id'] = fb['id']
  pc['accounts'] = [{'domain': ACCOUNT_DOMAIN, 'userid': fb['id']}]

  if 'username' in fb:
    pc['accounts'][0]['username'] = fb['username']

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
      # TODO: convert these to proper xs:date (ISO 8601)format, e.g.
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

  if '' in fb:
    pc[''] = fb['']

  return dict(pc)


application = webapp.WSGIApplication([
    # ('/facebook/add', AddFacebookPage),
    # ('/facebook/got_access_token', GotAccessToken),
    ], debug=appengine_config.DEBUG)

def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
