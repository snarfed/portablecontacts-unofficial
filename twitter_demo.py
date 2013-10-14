"""Twitter front page and OAuth demo handlers.
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

import urllib

import appengine_config
from oauth_dropins import twitter
import webapp2


class StartHandler(twitter.StartHandler):
  callback_path = '/oauth_callback'


class CallbackHandler(twitter.CallbackHandler):
  def finish(self, auth_entity, state=None):
    self.redirect('/?%s' % urllib.urlencode({
          'access_token_key': auth_entity.token_key,
          'access_token_secret': auth_entity.token_secret,
          }))


application = webapp2.WSGIApplication(
  [('/start_auth', StartHandler),
   ('/oauth_callback', CallbackHandler),
   ],
  debug=appengine_config.DEBUG)
