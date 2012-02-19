#!/usr/bin/python
"""Misc utilities.
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>'


def to_xml(value):
  """Renders a dict (usually from JSON) as an XML snippet.
  """
  # assert isinstance(value, dict)
  # if isinstance(value, (list, tuple)):
  #   return '\n'.join([to_xml(elem) for elem in value])
  if isinstance(value, dict):
    elems = []
    for key, vals in value.iteritems():
      if not isinstance(vals, (list, tuple)):
        vals = [vals]
      elems.extend(u'<%s>%s</%s>' % (key, to_xml(val), key) for val in vals)
    return '\n' + '\n'.join(elems) + '\n'
    # return '\n'.join(elems)
  else:
    return unicode(value) if value else ''
