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

from api import System


def runApp():
    system = System()
    system.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True  # 设置这一项是每次请求结束后都会自动提交数据库中的变动
    system.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:19850321@localhost:3306/api'

    system.run(debug=True, host='0.0.0.0')


if __name__ == '__main__':
    runApp()

