"""Serves the the front page, discovery files, and OAuth flows.

The discovery files inside /.well-known/ include host-meta (XRD), and
host-meta.xrds (XRDS-Simple), and host-meta.jrd (JRD ie JSON).

Note that XRDS-Simple is deprecated and superceded by XRD, but the
PortableContacts spec requires it specifically, so we support it as well as XRD.

http://portablecontacts.net/draft-spec.html
http://docs.oasis-open.org/xri/xrd/v1.0/xrd-1.0.html
http://hueniverse.com/drafts/draft-xrds-simple-01.html
"""

__author__ = 'Ryan Barrett <portablecontacts@ryanb.org>'

import urllib

import appengine_config
import poco
import webapp2
from webutil import handlers

from oauth_dropins import facebook
from oauth_dropins import twitter
site_module = {'facebook-poco': facebook,
               'twitter-poco': twitter,
               }[appengine_config.APP_ID]


class FrontPageHandler(handlers.TemplateHandler):
  """Renders and serves /, ie the front page.
  """
  def template_file(self):
    return poco.SOURCE.FRONT_PAGE_TEMPLATE

  def template_vars(self):
    return {'domain': poco.SOURCE.DOMAIN,
            'auth_url': poco.SOURCE.AUTH_URL,
            }

class CallbackHandler(site_module.CallbackHandler):
  def finish(self, auth_entity, state=None):
    return_params = {'facebook-poco': ('access_token',),
                     'twitter-poco': ('token_key', 'token_secret'),
                     }[appengine_config.APP_ID]

    self.redirect('/?%s' % urllib.urlencode(
        {k: getattr(auth_entity, k) for k in return_params}))


application = webapp2.WSGIApplication([
    ('/', FrontPageHandler),
    ('/start_auth', site_module.StartHandler.to('/oauth_callback')),
    ('/oauth_callback', CallbackHandler),
    ] + handlers.HOST_META_ROUTES,
  debug=appengine_config.DEBUG)
