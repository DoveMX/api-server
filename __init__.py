#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os


from flask import Flask
from flask_restful import Resource, Api

from gmagon.database import db
from gmagon.datainit import init as plugin_data_init
from gmagon.resources import install as plugin_resources_install


class System(Flask):
    """继承Flask，创建自定义类
    """

    def __init__(self, *args, **kwargs):
        print(u'System(Flask) ... ')
        super(self.__class__, self).__init__(__name__, static_folder=None, *args, **kwargs)
        self.configure()


    def version(self):
        return '1.0.1'

    def configure(self):
        '''
        查看帮助在线文档：http://www.pythondoc.com/flask-sqlalchemy/config.html
        '''
        self.config['BASEDIR'] = os.path.abspath(os.path.dirname(__file__))
        self.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

        # self.config['DEBUG'] = True  ## 开通Debug后，系统重启两次，这是正常的
        # self.config['HOST'] = '0.0.0.0'

    def init_database(self):
        print(u'init_database ... ')
        db.init_app(self)
        with self.app_context():
            db.create_all()

    def wsgi_app(self, environ, start_response):
        print(u'run custom Flask Class wsgi_app ... ')
        super(self.__class__, self).wsgi_app(environ, start_response)

    def run(self, host=None, port=None, debug=None, **options):
        print(u'run custom Flask Class run ... ')
        self.init_database()
        self.configRESTFULL()

        super(self.__class__, self).run(host=host, port=port, debug=debug, **options)

    def configRESTFULL(self):

        """
        ## flask-restful 中文返回的响应变成了 unicode literal
        解决方案
        指定 RESTFUL_JSON 配置项：
        app = Flask(__name__)
        app.config.update(RESTFUL_JSON=dict(ensure_ascii=False))
        """
        print(u'configRESTFULL ... ')

        self.config.update(RESTFUL_JSON=dict(ensure_ascii=False))

        api = Api(self)
        plugin_resources_install(api)
        plugin_data_init(api)
