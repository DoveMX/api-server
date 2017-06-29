#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os

try:
    virtenv = os.environ['OPENSHIFT_PYTHON_DIR'] + '/virtenv/'
    virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
    execfile(virtualenv, dict(__file__=virtualenv))
except IOError:
    pass
except Exception:
    pass

from app import app

## from run import app as application


if __name__ == '__main__':
    print('call main ...')
    app.run(debug=True, host='0.0.0.0')
