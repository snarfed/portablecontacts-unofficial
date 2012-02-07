#!/usr/bin/python
"""PortableContacts API handler classes.

TODO: xml
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

import json

import facebook
import twitter

from google.appengine.api import app_identity
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

try:
  APP_ID = app_identity.get_application_id()
except AttributeError:
  # this is probably a unit test
  APP_ID = None

# maps app id to source class
SOURCES = {
  'facebook-portablecontacts': facebook.Facebook,
  'twitter-portablecontacts': twitter.Twitter,
  }


class BaseHandler(webapp.RequestHandler):
  """Base class for PortableContacts API handlers.

  TODO: implement paging:
  file:///home/ryanb/docs/portablecontacts_spec.html#anchor14

  Attributes:
    source: Source subclass
  """

  def __init__(self):
    self.source = SOURCES[APP_ID](self)

  def make_response(self, contacts):
    """Args:
      contacts: list of PoCo contact dicts
    """
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps({
        'startIndex': 0,
        'itemsPerPage': 10,
        'totalResults': len(contacts),
        'entry': contacts,
        }))

class AllHandler(BaseHandler):
  """Returns all contacts.
  """
  def get(self):
    return self.make_response(self.source.get_contacts())


class SelfHandler(BaseHandler):
  """Returns the currently authenticated user's contact.
  """
  def get(self):
    return self.make_response(
        self.source.get_contacts(user_id=self.get_current_user_id()))


class UserIdHandler(BaseHandler):
  """Returns a single user's contact.
  """
  def get(self):
    return self.make_response(self.source.get_contacts(user_id=XXX))


def main():
  application = webapp.WSGIApplication(
      [('/poco/@me/@all/?', AllHandler),
       ('/poco/@me/@self/?', SelfHandler),
       ('/poco/@me/([0-9]+)/?', UserIdHandler),
       ],
      debug=appengine_config.DEBUG)
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
