#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import os
import traceback

################################################################
try:
    virtenv = os.environ['OPENSHIFT_PYTHON_DIR'] + '/virtenv/'
    virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
    execfile(virtualenv, dict(__file__=virtualenv))
except IOError:
    pass
except Exception:
    pass

from apiapp import app as application



