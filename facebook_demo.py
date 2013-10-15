"""Facebook front page and OAuth demo handlers.
"""

import appengine_config
from oauth_dropins import facebook
import webapp2


class StartHandler(facebook.StartHandler):
  callback_path = '/oauth_callback'


class CallbackHandler(facebook.CallbackHandler):
  callback_path = '/oauth_callback'

  def finish(self, auth_entity, state=None):
    self.redirect('/?access_token=%s' % auth_entity.access_token)


application = webapp2.WSGIApplication(
  [('/start_auth', StartHandler),
   ('/oauth_callback', CallbackHandler),
   ],
  debug=appengine_config.DEBUG)
