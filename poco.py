#!/usr/bin/python
"""PortableContacts API handler classes.
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

try:
  import json
except ImportError:
  import simplejson as json
import logging
import os
import webapp2
from webob import exc

import appengine_config
import facebook
import twitter
import util

from google.appengine.ext.webapp.util import run_wsgi_app

# maps app id to source class
SOURCE = {
  'facebook-poco': facebook.Facebook,
  'twitter-poco': twitter.Twitter,
  }.get(appengine_config.APP_ID)

XML_TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8"?>
<response>%s</response>
"""


class BaseHandler(webapp2.RequestHandler):
  """Base class for PortableContacts API handlers.

  TODO: implement paging:
  file:///home/ryanb/docs/portablecontacts_spec.html#anchor14

  Attributes:
    source: Source subclass
  """

  def __init__(self, *args, **kwargs):
    super(BaseHandler, self).__init__(*args, **kwargs)
    self.source = SOURCE(self)

  def get(self, user_id=None):
    """Args:
      contacts: list of PoCo contact dicts
    """
    kwargs = {}
    for param in 'startIndex', 'count':
      val = self.request.get(param, 0)
      try:
        val = int(val)
        assert val >= 0
        kwargs[param] = val
      except (ValueError, AssertionError):
        raise exc.HTTPBadRequest('Invalid %s: %s (should be positive int)' %
                                 (param, val))

    contacts = self.source.get_contacts(user_id, **kwargs)

    response = {'startIndex': kwargs['startIndex'],
                'itemsPerPage': self.source.ITEMS_PER_PAGE,
                'totalResults': len(contacts),
                'entry': contacts,
                'filtered': False,
                'sorted': False,
                'updatedSince': False,
                }

    format = self.request.get('format', 'json')
    if format == 'json':
      self.response.headers['Content-Type'] = 'application/json'
      self.response.out.write(json.dumps(response, indent=2))
    elif format == 'xml':
      self.response.headers['Content-Type'] = 'text/xml'
      self.response.out.write(XML_TEMPLATE % util.to_xml(response))
    else:
      raise exc.HTTPBadRequest('Invalid format: %s (should be json or xml)' %
                               format)


class AllHandler(BaseHandler):
  """Returns all contacts.
  """
  def get(self):
    super(AllHandler, self).get()


class SelfHandler(BaseHandler):
  """Returns the currently authenticated user's contact.
  """
  def get(self):
    super(SelfHandler, self).get(user_id=self.source.get_current_user())


class UserIdHandler(BaseHandler):
  """Returns a single user's contact.
  """
  def get(self, user_id):
    super(UserIdHandler, self).get(user_id=int(user_id))


application = webapp2.WSGIApplication(
    # based on the poco spec: http://portablecontacts.net/draft-spec.html#anchor11
    [('/poco/?', AllHandler),
     ('/poco/@me/@all/?', AllHandler),
     ('/poco/@me/@all/([0-9]+)/?', UserIdHandler),
     ('/poco/@me/@self/?', SelfHandler),
     ],
    debug=appengine_config.DEBUG)

def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
