#!/usr/bin/env python
"""Serves the app.

Includes the PortableContacts API, the descriptive HTML front page, and the
/.well-known/* files, including both XRD host-meta and XRDS-Simple
host-meta.xrds.

http://portablecontacts.net/draft-spec.html

Note that XRDS-Simple is deprecated and superceded by XRD, but the
PortableContacts spec requires it specifically, so we support it as well as XRD.

http://docs.oasis-open.org/xri/xrd/v1.0/xrd-1.0.html
http://hueniverse.com/drafts/draft-xrds-simple-01.html
"""

__author__ = 'Ryan Barrett <portablecontacts@ryanb.org>'
import logging
import os
import urlparse

import appengine_config
import poco

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

# Included in most static HTTP responses.
BASE_HEADERS = {
  'Cache-Control': 'max-age=300',
  'X-XRDS-Location': 'https://%s/.well-known/host-meta.xrds' %
    appengine_config.HOST,
  }
BASE_TEMPLATE_VARS = {
  'domain': poco.SOURCE.DOMAIN,
  'host': appengine_config.HOST,
  }

# FRONT_PAGE_HANDLER = {
#   'facebook-portablecontacts': facebook_demo.FrontPageHandler,
#   'twitter-portablecontacts': twitter_demo.FrontPageHandler,
#   }.get(appengine_config.APP_ID)


class TemplateHandler(webapp.RequestHandler):
  """Renders and serves a template based on class attributes.

  Subclasses must override at least template_file.

  Attributes:
    template_vars: dict

  Class attributes:
    content_type: string
    template: path to template file
  """
  content_type = 'text/html'
  template_file = None

  def __init__(self, *args, **kwargs):
    self.template_vars = dict(BASE_TEMPLATE_VARS)
    super(TemplateHandler, self).__init__(*args, **kwargs)

  def get(self):
    self.response.headers['Content-Type'] = self.content_type
    # can't update() because wsgiref.headers.Headers doesn't have it.
    for key, val in BASE_HEADERS.items():
      self.response.headers[key] = val
    self.response.out.write(template.render(self.template_file,
                                            self.template_vars))


# class FrontPageHandler(TemplateHandler):
#   """Renders and serves /, ie the front page.
#   """
#   content_type = 'text/html'
#   template_file = os.path.join('templates', INDEX_TEMPLATE)


class HostMetaXrdHandler(TemplateHandler):
  """Renders and serves the /.well-known/host-meta XRD file.
  """
  content_type = 'application/xrd+xml'
  template_file = 'templates/host-meta.xrd'


class HostMetaXrdsHandler(TemplateHandler):
  """Renders and serves the /.well-known/host-meta.xrds XRDS-Simple file.
  """
  content_type = 'application/xrds+xml'
  template_file = 'templates/host-meta.xrds'


def main():
  application = webapp.WSGIApplication(
      [('/.well-known/host-meta', HostMetaXrdHandler),
       ('/.well-known/host-meta.xrds', HostMetaXrdsHandler),
       ],
      debug=appengine_config.DEBUG)
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
