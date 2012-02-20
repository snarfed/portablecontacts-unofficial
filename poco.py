#!/usr/bin/python
"""PortableContacts API handler classes.

STATE: built in webapp doesn't have exception handler. (WSGIApplication doesn't
have error_handlers attr.) bring in webapp2 which does.
then finish xml tests, then paging, etc.
TODO: xml
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

import json
import logging
import os
from webob import exc

import appengine_config
import facebook
import twitter
import util

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

# maps app id to source class
SOURCE = {
  'facebook-portablecontacts': facebook.Facebook,
  'twitter-portablecontacts': twitter.Twitter,
  }.get(appengine_config.APP_ID)

XML_TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8"?>
<response>%s</response>
"""

class BaseHandler(webapp.RequestHandler):
  """Base class for PortableContacts API handlers.

  TODO: implement paging:
  file:///home/ryanb/docs/portablecontacts_spec.html#anchor14

  Attributes:
    source: Source subclass
  """

  def __init__(self, *args, **kwargs):
    super(BaseHandler, self).__init__(*args, **kwargs)
    self.source = SOURCE(self)

  def make_response(self, contacts):
    """Args:
      contacts: list of PoCo contact dicts
    """
    response = {'startIndex': 0,
                'itemsPerPage': 10,
                'totalResults': len(contacts),
                'entry': contacts,
                }

    format = self.request.get('format', 'json')
    if format == 'json':
      self.response.headers['Content-Type'] = 'application/json'
      self.response.out.write(json.dumps(response, indent=2))
    elif format == 'xml':
      self.response.headers['Content-Type'] = 'text/xml'
      self.response.out.write(XML_TEMPLATE % util.to_xml(response))
    else:
      self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
      e = exc.HTTPBadRequest('Invalid format: %s (should be json or xml)' %
                                format)
      self.response.out.write(str(self.request.get_response(e)).strip())


class AllHandler(BaseHandler):
  """Returns all contacts.
  """
  def get(self):
    self.make_response(self.source.get_contacts())


class SelfHandler(BaseHandler):
  """Returns the currently authenticated user's contact.
  """
  def get(self):
    self.make_response(self.source.get_contacts(
        user_id=self.source.get_current_user()))


class UserIdHandler(BaseHandler):
  """Returns a single user's contact.
  """
  def get(self, user_id):
    self.make_response(self.source.get_contacts(user_id=int(user_id)))


application = webapp.WSGIApplication(
    # based on the poco spec: http://portablecontacts.net/draft-spec.html#anchor11
    [('/poco/?', AllHandler),
     # quote the @s :/ but only in python 2.5, not in 2.7...?
     ('/poco/%40me/%40all/?', AllHandler),
     ('/poco/%40me/%40all/([0-9]+)/?', UserIdHandler),
     ('/poco/%40me/%40self/?', SelfHandler),
     ],
    debug=appengine_config.DEBUG)

def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
