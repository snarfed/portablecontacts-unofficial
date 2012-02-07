#!/usr/bin/python
"""Source base class.
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

import json
from webob import exc

from google.appengine.api import urlfetch


class Source(object):
  """Abstract base class for a source (e.g. Facebook, Twitter).

  Concrete subclasses must override DOMAIN and implement get_contacts() and
  get_current_user_id().

  OAuth credentials may be extracted from the current request's HTTP headers,
  e.g. 'Authentication', or query parameters, e.g. access_token for Facebook.

  TODO: implement paging:
  file:///home/ryanb/docs/portablecontacts_spec.html#anchor14

  Attributes:
    handler: the current RequestHandler

  Class constants:
    DOMAIN: the source's domain
  """

  DOMAIN = None

  def __init__(self, handler):
    self.handler = handler

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
        self.handler.response.headers[key] = val
      self.handler.response.out.write(resp.content)
      raise exc.status_map.get(resp.status_code)(resp.content)
