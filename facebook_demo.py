#!/usr/bin/python
"""Facebook front page and OAuth demo handlers.
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

import logging
import urllib
from webob import exc

import appengine_config
import facebook

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


class FrontPageHandler(TemplateHandler):
  """Renders and serves /, ie the front page.
  """
  template_file = 'templates/facebook_index.html'


class CallbackHandler(webapp.RequestHandler):
  """The OAuth callback. Fetches an access token and redirects to the front page.
  """

  def get(self):
    oauth_token = self.request.get('oauth_token', None)
    oauth_verifier = self.request.get('oauth_verifier', None)
    if oauth_token is None:
      raise exc.HTTPBadRequest('Missing required query parameter oauth_token.')

    # Lookup the request token
    request_token = OAuthToken.gql('WHERE token_key=:key', key=oauth_token).get()
    if request_token is None:
      raise exc.HTTPBadRequest('Invalid oauth_token: %s' % oauth_token)

    # Rebuild the auth handler
    auth = tweepy.OAuthHandler(appengine_config.TWITTER_APP_KEY,
                               appengine_config.TWITTER_APP_SECRET)
    auth.set_request_token(request_token.token_key, request_token.token_secret)

    # Fetch the access token
    try:
      access_token = auth.get_access_token(oauth_verifier)
    except tweepy.TweepError, e:
      msg = 'Twitter OAuth error, could not get access token: '
      logging.exception(msg)
      raise exc.HTTPInternalServerError(msg + `e`)

    params = {'access_token_key': access_token.key,
              'access_token_secret': access_token.secret,
              }
    self.redirect('/?%s' % urllib.urlencode(params))


def main():
  application = webapp.WSGIApplication(
      [('/oauth_callback', CallbackHandler),
       ],
      debug=appengine_config.DEBUG)
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
