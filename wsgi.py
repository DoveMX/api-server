#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import os
import traceback

################################################################
app_for_rhc = False
try:
    virtenv = os.environ['OPENSHIFT_PYTHON_DIR'] + '/virtenv/'
    virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
    execfile(virtualenv, dict(__file__=virtualenv))
    app_for_rhc = True
except IOError:
    pass
except Exception:
    pass

if app_for_rhc:
    from apiapp import app as application
else:
    from apiapp import runApp
    runApp()




