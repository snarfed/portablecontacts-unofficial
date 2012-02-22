#!/usr/bin/python
"""Source base class.
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

try:
  import json
except ImportError:
  import simplejson as json
import logging
from webob import exc

from google.appengine.api import urlfetch


class Source(object):
  """Abstract base class for a source (e.g. Facebook, Twitter).

  Concrete subclasses must override DOMAIN and implement get_contacts() and
  get_current_user().

  OAuth credentials may be extracted from the current request's query parameters
  e.g. access_token_key and access_token_secret for Twitter (OAuth 1.0a) and
  access_token for Facebook (OAuth 2.0).

  Attributes:
    handler: the current RequestHandler

  Class constants:
    DOMAIN: string, the source's domain
    ITEMS_PER_PAGE: int, the default number of contacts returned per request
    FRONT_PAGE_TEMPLATE: string, the front page child template filename
    AUTH_URL = string, the url for the "Authenticate" front page link
  """

  def __init__(self, handler):
    self.handler = handler

  def get_contacts(self, user_id=None, startIndex=0, count=0):
    """Return a (Python) list of PoCo contacts to be JSON-encoded.

    If user_id is provided, only that user's contact(s) are included.
    startIndex and count determine paging, as described in the spec:
    http://portablecontacts.net/draft-spec.html#anchor14

    Args:
      user_id: int
      startIndex: int >= 0
      count: int >= 0
    """
    raise NotImplementedError()

  def get_current_user(self):
    """Returns the current (authed) user, either integer id or string username.
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
    logging.debug('Fetching %s with kwargs %s', url, kwargs)
    resp = urlfetch.fetch(url, deadline=999, **kwargs)

    if resp.status_code == 200:
      return resp.content
    else:
      logging.warning('GET %s returned %d:\n%s',
                      url, resp.status_code, resp.content)
      self.handler.response.headers.update(resp.headers)
      self.handler.response.out.write(resp.content)
      raise exc.status_map.get(resp.status_code)(resp.content)
