#!/usr/bin/python
"""Source base class.
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']


class Source(object):
  """Abstract base class for a source (e.g. Facebook, Twitter).

  Concrete subclasses must override DOMAIN and implement get_contacts() and
  get_current_user().

  Class constants:
    DOMAIN: string, the source's domain
    FRONT_PAGE_TEMPLATE: string, the front page child template filename
    AUTH_URL = string, the url for the "Authenticate" front page link
  """

  def get_contacts(self, user_id=None, start_index=0, count=0):
    """Return a list and total count of PoCo contacts.

    If user_id is provided, only that user's contact(s) are included.
    start_index and count determine paging, as described in the spec:
    http://portablecontacts.net/draft-spec.html#anchor14

    Args:
      user_id: int
      start_index: int >= 0
      count: int >= 0

    Returns:
      (total_results, contacts) tuple
      total_results: int or None (e.g. if it can't be calculated efficiently)
      contacts: list of contact dicts to be JSON-encoded
    """
    raise NotImplementedError()

  def get_current_user(self):
    """Returns the current (authed) user, either integer id or string username.
    """
    raise NotImplementedError()
