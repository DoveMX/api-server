#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
G_ENABLE_RESETENCODING = True # 是否开启重新设置默认编码
if G_ENABLE_RESETENCODING:
    #Python IDLE reload(sys)后无法正常执行命令的原因
    #http://www.2cto.com/kf/201411/355112.html
    G_stdi,G_stdo,G_stde=sys.stdin,sys.stdout,sys.stderr
    if sys.version_info.major < 3:
        reload(sys)
        sys.setdefaultencoding('utf8')
        sys.stdin,sys.stdout,sys.stderr = G_stdi,G_stdo,G_stde

    print('system-default-encoding: ' + sys.getdefaultencoding())

import traceback

### 添加自定义目录到Python的运行环境中
CUR_DIR_NAME = os.path.dirname(__file__)
def g_add_path_to_sys_paths(path):
    if os.path.exists(path):
        print('Add myself packages = %s' % path)
        sys.path.extend([path]) #规范Windows或者Mac的路径输入

try:
    curPath = os.path.normpath(os.path.abspath(CUR_DIR_NAME))
    path1 = os.path.normpath(os.path.abspath(os.path.join(CUR_DIR_NAME, 'self-site')))
    path2 = os.path.normpath(os.path.abspath(os.path.join(CUR_DIR_NAME, 'rs/self-site')))

    pathList = [curPath, path1, path2]
    for path in pathList:
        g_add_path_to_sys_paths(path)

    ##添加"",当前目录.主要是与标准Python的路径相对应.
    if '' not in sys.path:
        sys.path.insert(0,'')

except Exception as e:
    pass

### [End] 添加自定义目录到Python的运行环境中
print('sys.path =', sys.path)



################################################################
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
from system import System

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
    system.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:19850321db@localhost:3306/api'

    # 自动创建数据库
    create_database()

    system.run(debug=True, host='0.0.0.0')


if __name__ == '__main__':
    runApp()

