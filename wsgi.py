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
from sqlalchemy_utils import database_exists as su_database_exists, \
    drop_database as su_drop_database, create_database as su_create_database

# local
from api import System

system = System()


@system.route('/')
def hello_world():
    return u'Hello Gmagon'

@system.route('/admin_gmagon/db/drop')
def drop_database():
    if su_database_exists(system.config['SQLALCHEMY_DATABASE_URI']):
        su_drop_database(system.config['SQLALCHEMY_DATABASE_URI'])
        return u'database be removed...'
    else:
        return u'database not exit'

@system.route('/admin_gmagon/db/create')
def create_database():
    if not su_database_exists(system.config['SQLALCHEMY_DATABASE_URI']):
        su_create_database(system.config['SQLALCHEMY_DATABASE_URI'])
        return u'create database...'
    else:
        return u'database is exist'

def runApp():
    system.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True  # 设置这一项是每次请求结束后都会自动提交数据库中的变动
    system.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:19850321@localhost:3306/api'

    # 自动创建数据库
    create_database()

    system.run(debug=True, host='0.0.0.0')


if __name__ == '__main__':
    runApp()

