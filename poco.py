#!/usr/bin/python
"""PortableContacts API handler classes.

TODO: xml
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

import json
import logging
import os

import appengine_config
import facebook
import twitter

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

# maps app id to source class
SOURCE = {
  'facebook-portablecontacts': facebook.Facebook,
  'twitter-portablecontacts': twitter.Twitter,
  }.get(appengine_config.APP_ID)


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
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps({
        'startIndex': 0,
        'itemsPerPage': 10,
        'totalResults': len(contacts),
        'entry': contacts,
        },
        indent=2))  # pretty-print

class AllHandler(BaseHandler):
  """Returns all contacts.
  """
  def get(self):
    logging.warning('all')
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
     ('/poco/%40me/%40all/?', AllHandler),
     ('/poco/%40me/%40all/([0-9]+)/?', UserIdHandler),
     ('/poco/%40me/%40self/?', SelfHandler),
     ],
    debug=appengine_config.DEBUG)

def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
