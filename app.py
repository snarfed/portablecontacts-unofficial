#!/usr/bin/env python
"""Serves the HTML front page and discovery files.

The discovery files inside /.well-known/ include host-meta (XRD), and
host-meta.xrds (XRDS-Simple), and host-meta.jrd (JRD ie JSON).

Note that XRDS-Simple is deprecated and superceded by XRD, but the
PortableContacts spec requires it specifically, so we support it as well as XRD.

http://portablecontacts.net/draft-spec.html
http://docs.oasis-open.org/xri/xrd/v1.0/xrd-1.0.html
http://hueniverse.com/drafts/draft-xrds-simple-01.html
"""

__author__ = 'Ryan Barrett <portablecontacts@ryanb.org>'

import appengine_config
import poco
from webutil import handlers

import webapp2

class FrontPageHandler(handlers.TemplateHandler):
  """Renders and serves /, ie the front page.
  """
  def template_file(self):
    return poco.SOURCE.FRONT_PAGE_TEMPLATE

  def template_vars(self):
    return {'domain': poco.SOURCE.DOMAIN,
            'auth_url': poco.SOURCE.AUTH_URL,
            }


application = webapp2.WSGIApplication(
  [('/', FrontPageHandler)] + handlers.HOST_META_ROUTES,
  debug=appengine_config.DEBUG)
