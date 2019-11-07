#!/usr/bin/env python

import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/var/www/html/catalog/catalog/')
from application import app as application
application.secret_key = 'super_secret_key'
