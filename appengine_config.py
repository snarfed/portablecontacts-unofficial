"""App Engine settings.
"""

import os

# app_identity.get_default_version_hostname() would be better here, but
# it doesn't work in dev_appserver since that doesn't set
# os.environ['DEFAULT_VERSION_HOSTNAME'].
HOST = os.getenv('HTTP_HOST')

TWITTER_APP_KEY = '1BsluYKc6dSRdI07VPTUhA'
with open('twitter_app_secret') as f:
  TWITTER_APP_SECRET = f.read().strip()

if not os.environ.get('SERVER_SOFTWARE', '').startswith('Development'):
  DEBUG = False
  MOCKFACEBOOK = False
else:
  DEBUG = True
  MOCKFACEBOOK = False
