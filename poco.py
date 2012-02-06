#!/usr/bin/python
"""PocoHandler base class.

TODO: xml
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

import json
import logging

from webob import exc

import appengine_config

from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


class PocoHandler(webapp.RequestHandler):
  """Abstract base handler class for PortableContacts API.

  Concrete subclasses must implement get_contacts() and get_current_user_id().

  OAuth credentials may be extracted from the current request's HTTP headers,
  e.g. 'Authentication', or query parameters, e.g. access_token for Facebook.

  TODO: implement paging:
  file:///home/ryanb/docs/portablecontacts_spec.html#anchor14
  """

  def get(self):
    contacts = self.get_contacts()

    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps({
        'startIndex': 0,
        'itemsPerPage': 10,
        'totalResults': len(contacts),
        'entry': contacts,
        }))

  def get_contacts(self, user_id=None):
    """Return a (Python) list of PoCo contacts to be JSON-encoded.

    If user_id is provided, only that user's contact(s) are included.

    Args:
      user_id: int
    """
    raise NotImplementedError()

  def get_current_user_id(self):
    """Returns the currently authenticated user's id (an integer).
    """
    raise NotImplementedError()

  def urlfetch(self, url, **kwargs):
    """Wraps urlfetch. Passes error responses through to the client.

    ...by raising HTTPException.

    Args:
      url: str
      kwargs: passed through to urlfetch.fetch()

    Returns:
      the HTTP response body
    """
    resp = urlfetch.fetch(url, deadline=999, **kwargs)

    if resp.status_code == 200:
      return resp.content
    else:
      # can't update() because webapp.Response.headers isn't a dict and doesn't
      # have it
      for key, val in resp.headers.items():
        self.response.headers[key] = val
      self.response.out.write(resp.content)
      raise exc.status_map.get(resp.status_code)(resp.content)
