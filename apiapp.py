#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

import os

print("\n app begin... \n")

G_ENABLE_RESETENCODING = True  # 是否开启重新设置默认编码
if G_ENABLE_RESETENCODING:
    # Python IDLE reload(sys)后无法正常执行命令的原因
    # http://www.2cto.com/kf/201411/355112.html
    G_stdi, G_stdo, G_stde = sys.stdin, sys.stdout, sys.stderr
    if sys.version_info.major < 3:
        reload(sys)
        sys.setdefaultencoding('utf8')
        sys.stdin, sys.stdout, sys.stderr = G_stdi, G_stdo, G_stde

    print('system-default-encoding: ' + sys.getdefaultencoding())

### 添加自定义目录到Python的运行环境中
CUR_DIR_NAME = os.path.dirname(__file__)


def g_add_path_to_sys_paths(path):
    if os.path.exists(path):
        print('Add myself packages = %s' % path)
        sys.path.extend([path])  # 规范Windows或者Mac的路径输入


try:
    curPath = os.path.normpath(os.path.abspath(CUR_DIR_NAME))
    path1 = os.path.normpath(os.path.abspath(os.path.join(CUR_DIR_NAME, 'self-site')))
    path2 = os.path.normpath(os.path.abspath(os.path.join(CUR_DIR_NAME, 'rs/self-site')))

    pathList = [curPath, path1, path2]
    for path in pathList:
        g_add_path_to_sys_paths(path)

    ##添加"",当前目录.主要是与标准Python的路径相对应.
    if '' not in sys.path:
        sys.path.insert(0, '')

except Exception as e:
    pass

### [End] 添加自定义目录到Python的运行环境中
print('sys.path =', sys.path)

print(u"[X] import sqlalchemy_utils")

# lib
from sqlalchemy_utils import database_exists as su_database_exists, \
    drop_database as su_drop_database, create_database as su_create_database
from flask_cors import CORS

print(u"[X] import System")

# local
from apiflask import APIFlask

# 创建唯一实例
# app = Flask(__name__.split('.')[0])
app = APIFlask(__name__.split('.')[0])

# 支持CORS
CORS(app)

# Step1: 配置

mysql_server_url = "mysql://root:19850321db@localhost:3306/"  # 获取远程服务器上的账号及密码
try:
    mysql_server_url = os.environ['OPENSHIFT_MYSQL_DB_URL']
except Exception, e:
    print(e.message)

# 配置系统
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True  # 设置这一项是每次请求结束后都会自动提交数据库中的变动
app.config['SQLALCHEMY_DATABASE_URI'] = mysql_server_url + 'api'
app.config['threaded'] = True

"""
## flask-restful 中文返回的响应变成了 unicode literal
解决方案
指定 RESTFUL_JSON 配置项：
app = Flask(__name__)
app.config.update(RESTFUL_JSON=dict(ensure_ascii=False))
"""
print(u'[X] configRESTFULL ... ')

app.config.update(RESTFUL_JSON=dict(ensure_ascii=False))

# Step2: 配置路由
print(u"[X] defined some admin route..")

rAdmin = '/admin_gmagon'


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


@app.route('/')
def hello_world():
    return u'Hello Gmagon'


@app.route(rAdmin + '/db/drop')
def drop_database():
    if su_database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
        su_drop_database(app.config['SQLALCHEMY_DATABASE_URI'])
        return u'database be removed...'
    else:
        return u'database not exit'


@app.route(rAdmin + '/db/create')
def create_database():
    if not su_database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
        su_create_database(app.config['SQLALCHEMY_DATABASE_URI'])
        return u'create database...'
    else:
        return u'database is exist'


@app.route(rAdmin + '/db/isexist')
def database_is_exist():
    if not su_database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
        return u'[not exist] =' + app.config['SQLALCHEMY_DATABASE_URI']
    else:
        return u'[exist] =' + app.config['SQLALCHEMY_DATABASE_URI']



# 3. 启动前的最后准备
create_database()  # 创建数据库，如果数据库不存在的情况下
app.before_run()  # app run 之前需要调用支持插件配置等操作

"""
Test
"""


def run_app_for_test():
    print("[X] runApp begin...")

    # 获取IP地址、端口及主机名称
    ip = '0.0.0.0'
    port = 5000
    server_enable_debug = True  # 是否开启服务器调试

    # 打印一些关键的数据
    print('\nip=%s, port=%d' % (ip, port))
    print('mysql_server_url = %s' % mysql_server_url)

    # 启动系统
    app.run(debug=server_enable_debug, host=ip, port=port)
