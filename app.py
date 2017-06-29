#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask

# local
from core.database import db
from core.g_orm_def import *
from core.gif.orm_def import *
from core.gif.data_init import init_all as gif_data_init


## ---------------------
app = Flask(__name__)

print('call Flask ...')
'''
查看帮助在线文档：http://www.pythondoc.com/flask-sqlalchemy/config.html
'''
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:19850321@localhost:3306/api'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True #设置这一项是每次请求结束后都会自动提交数据库中的变动
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True


@app.before_first_request
def create_tables():
    db.create_all()
    gif_data_init()

@app.route('/')
def index():
    return 'Index Page'


@app.route('/services/gif/')
def services_gif_index():
    return "It's gif services"

# 数据自动采集接口


@app.route('/da/gif/start/')
def da_gif_start():
    return "It's gif data acquisition engine"


if __name__ == '__main__':
    db.init_app(app)
    app.run()