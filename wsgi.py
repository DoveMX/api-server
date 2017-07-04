#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os

import sys
if sys.version_info.major < 3:
    reload(sys)
sys.setdefaultencoding('utf-8')
print('system-default-encoding: ' + sys.getdefaultencoding())

try:
    virtenv = os.environ['OPENSHIFT_PYTHON_DIR'] + '/virtenv/'
    virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
    execfile(virtualenv, dict(__file__=virtualenv))
except IOError:
    pass
except Exception:
    pass

# lib
from sqlalchemy_utils import database_exists, drop_database, create_database

# local
from api import System

system = System()

__db_uri = 'mysql://root:19850321@localhost:3306/api'


@system.route('/')
def hello_world():
    return u'HelloWorld你好'

@system.route('/admin/db/drop')
def drop_database():
    if database_exists(__db_uri):
        drop_database(__db_uri)

@system.route('/admin/db/create')
def create_database():
    if not database_exists(__db_uri):
        create_database(__db_uri)

def runApp():
    system.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True  # 设置这一项是每次请求结束后都会自动提交数据库中的变动
    system.config['SQLALCHEMY_DATABASE_URI'] = __db_uri

    system.run(debug=True, host='0.0.0.0')


if __name__ == '__main__':
    runApp()

