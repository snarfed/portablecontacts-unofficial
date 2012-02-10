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


class TemplateHandler(webapp.RequestHandler):
  """Renders and serves a template based on class attributes.

  Class attributes:
    content_type: string
    template: path to template file
  """
  content_type = None
  template_file = None

  def get(self):
    self.response.headers.update(BASE_HEADERS)
    self.response.headers['Content-Type'] = self.content_type
    self.response.out.write(template.render(self.template_file,
                                            BASE_TEMPLATE_VARS))


class FrontPageHandler(TemplateHandler):
  """Renders and serves /, ie the front page.
  """
  content_type = 'text/html'
  template_file = 'templates/index.html'


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
      [('/', FrontPageHandler),
       ('/.well-known/host-meta', HostMetaXrdHandler),
       ('/.well-known/host-meta.xrds', HostMetaXrdsHandler),
       ],
      debug=appengine_config.DEBUG)
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
