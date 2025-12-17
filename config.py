# OPENREVIEW CREDENTIALS
#
# Values can be provided via environment variables (`OPENREVIEW_EMAIL`,
# `OPENREVIEW_PASSWORD`, `OPENREVIEW_TOKEN`). If those aren't set you can
# uncomment the assignments at the bottom of the file and enter your
# credentials directly.

import os

EMAIL = os.environ.get('OPENREVIEW_EMAIL')
PASSWORD = os.environ.get('OPENREVIEW_PASSWORD')
TOKEN = os.environ.get('OPENREVIEW_TOKEN')

# Uncomment and fill if you prefer to keep credentials locally instead of
# environment variables.
# EMAIL = 'user@example.com'
# PASSWORD = 'replace-me'
# TOKEN = ''
