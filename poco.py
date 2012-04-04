#!/usr/bin/python
"""PortableContacts API handler classes.

http://portablecontacts.net/draft-spec.html
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
from webutil import util

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
ITEMS_PER_PAGE = 100


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
    paging_params = self.get_paging_params()
    total_results, contacts = self.source.get_contacts(user_id, **paging_params)

    response = {'startIndex': paging_params['start_index'],
                'itemsPerPage': len(contacts),
                'totalResults': total_results,
                'entry': contacts,
                'filtered': False,
                'sorted': False,
                'updatedSince': False,
                }

    self.response.headers['Access-Control-Allow-Origin'] = '*'

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

  def get_paging_params(self):
    """Extracts, normalizes and returns the startIndex and count query params.

    Returns:
      dict with 'start_index' and 'count' keys mapped to integers
    """
    start_index = self.get_positive_int('startIndex')
    count = self.get_positive_int('count')

    if count == 0:
      count = ITEMS_PER_PAGE - start_index
    else:
      count = min(count, ITEMS_PER_PAGE)

    return {'start_index': start_index, 'count': count}

  def get_positive_int(self, param):
    try:
      val = self.request.get(param, 0)
      val = int(val)
      assert val >= 0
      return val
    except (ValueError, AssertionError):
      raise exc.HTTPBadRequest('Invalid %s: %s (should be positive int)' %
                               (param, val))


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
