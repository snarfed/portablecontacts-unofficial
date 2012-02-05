"""App Engine settings.
"""

import os
  
try:
  if not os.environ.get('SERVER_SOFTWARE', '').startswith('Development'):
    DEBUG = False
    MOCKFACEBOOK = False
    # separate prod and devel facebook app ids since they need separate redirect
    # URL hostnames.
    FACEBOOK_APP_ID = '235997716482623'
    with open('facebook_app_secret_poco') as f:
      FACEBOOK_APP_SECRET = f.read().strip()
  else:
    DEBUG = True
    MOCKFACEBOOK = False
    FACEBOOK_APP_ID = '350503391634422'
    with open('facebook_app_secret_poco-local') as f:
      FACEBOOK_APP_SECRET = f.read().strip()

except IOError, e:
  # someone's probably running the tests and hasn't provided an app secret file.
  logging.warning('Missing facebook app secret file!')
  logging.exception(e)
