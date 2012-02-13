#!/usr/bin/python
"""Facebook front page and OAuth demo handlers.
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

import app
import appengine_config

from google.appengine.ext import webapp
from google.appengine.ext import db

CALLBACK = 'http://%s/oauth/callback' % appengine_config.HOST


class FrontPageHandler(app.TemplateHandler):
  """Renders and serves the front page.
  """

  def get(self):
    # Build a new oauth handler and display authorization url to user.
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK)
    try:
      print template.render('oauth_example/main.html', {
          'authurl': auth.get_authorization_url(),
          'request_token': auth.request_token
      })
    except tweepy.TweepError, e:
      # Failed to get a request token
      print template.render('twitter_error.html', {'message': e})
      return

    # We must store the request token for later use in the callback page.
    request_token = OAuthToken(
        token_key = auth.request_token.key,
        token_secret = auth.request_token.secret
    )
    request_token.put()


class CallbackPage(RequestHandler):
  """The OAuth callback.
  """

  def get(self):
    pass


def main():
  application = webapp.WSGIApplication(
      [('/', FrontPageHandler),
       ('/facebook_oauth_callback', CallbackHandler),
       ],
      debug=appengine_config.DEBUG)
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
