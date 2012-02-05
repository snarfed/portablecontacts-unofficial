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

__author__ = 'Ryan Barrett <portablecontacts-unofficial@ryanb.org>'

import appengine_config

import logging
import os
import urlparse

import facebook
import twitter

from google.appengine.api import app_identity
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

APP_ID = app_identity.get_application_id()

# maps app id to handler module
APP_ID_HANDLERS = {
  'facebook-portablecontacts': facebook.PocoHandler,
  'twitter-portablecontacts': twitter.PocoHandler,
  }
POCO_HANDLER = APP_ID_HANDLERS[APP_ID]

# app_identity.get_default_version_hostname() would be better here, but
# it doesn't work in dev_appserver since that doesn't set
# os.environ['DEFAULT_VERSION_HOSTNAME'].
HOST = os.getenv('HTTP_HOST')

# Included in most static HTTP responses.
BASE_HEADERS = {
  'Cache-Control': 'max-age=300',
  'X-XRDS-Location': 'https://%s/.well-known/host-meta.xrds' % HOST,
  }
BASE_TEMPLATE_VARS = {
  'domain': DOMAIN,
  'host': HOST,
  }


class TemplateHandler(webapp.RequestHandler):
  """Renders and serves a template based on class attributes.

  Class attributes:
    contenttype: string
    template: path to template file
  """
  contenttype = None
  template_file = None

  def get(self):
    self.response.headers.update(BASE_HEADERS)
    self.response.headers['Content-Type'] = self.contenttype
    self.response.out.write(template.render(self.template_file,
                                            BASE_TEMPLATE_VARS))


class FrontPageHandler(TemplateHandler):
  """Renders and serves /, ie the front page.
  """
  contenttype = 'text/html'
  template_file = 'templates/index.html'


class HostMetaXrdHandler(TemplateHandler):
  """Renders and serves the /.well-known/host-meta XRD file.
  """
  contenttype = 'application/xrd+xml'
  template_file = 'templates/host-meta.xrd'


class HostMetaXrdsHandler(TemplateHandler):
  """Renders and serves the /.well-known/host-meta.xrds XRDS-Simple file.
  """
  contenttype = 'application/xrds+xml'
  template_file = 'templates/host-meta.xrds'


class PocoHandler(webapp.RequestHandler):
  """Serves the PortableContacts API.
  """
  def get(self):
    # parse and validate user uri
    uri = self.request.get('uri')
    if not uri:
      raise webapp.exc.HTTPBadRequest('Missing uri query parameter.')

    parsed = urlparse.urlparse(uri)
    if parsed.scheme and parsed.scheme != 'acct':
      raise webapp.exc.HTTPBadRequest('Unsupported URI scheme: %s' % parsed.scheme)

    try:
      username, host = parsed.path.split('@')
      assert username, host
    except ValueError, AssertionError:
      raise webapp.exc.HTTPBadRequest('Bad user URI: %s' % uri)

    if host not in (HOST, DOMAIN):
      raise webapp.exc.HTTPBadRequest(
        'User URI %s has unsupported host %s; expected %s or %s.' %
        (uri, host, HOST, DOMAIN))

    # render template
    vars = {'uri': uri}
    vars.update(self.get_template_vars(username))

    self.response.headers['Content-Type'] = 'application/xrd+xml'
    self.response.headers['Cache-Control'] = 'max-age=300'
    self.response.out.write(template.render('templates/user.xrd', vars))

  def get_template_vars(self, username):
    if APP_ID == 'facebook-portablecontacts':
      return {
          'profile_url': 'http://www.facebook.com/%s' % username,
          'picture_url': 'http://graph.facebook.com/%s/picture' % username,
          'openid_url': 'http://facebook-openid.appspot.com/%s' % username,
          }
    elif APP_ID == 'twitter-portablecontacts':
      return {
          'profile_url': 'http://twitter.com/%s' % username,
          'picture_url':
            'http://api.twitter.com/1/users/profile_image?screen_name=%s' % username,
          }
    else:
      raise webapp.exc.HTTPInternalServerError('Unknown app id %s.' % APP_ID)

    return vars


def main():
  application = webapp.WSGIApplication(
      [('/', FrontPageHandler),
       ('/.well-known/host-meta', HostMetaXrdHandler),
       ('/.well-known/host-meta.xrds', HostMetaXrdsHandler),
       ('/poco/.*', POCO_HANDLER),
       ],
      debug=appengine_config.DEBUG)
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
