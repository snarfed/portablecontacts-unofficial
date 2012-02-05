"""App Engine settings.
"""

import os
  
if not os.environ.get('SERVER_SOFTWARE', '').startswith('Development'):
  DEBUG = False
  MOCKFACEBOOK = False
else:
  DEBUG = True
  MOCKFACEBOOK = False
