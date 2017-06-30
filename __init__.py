#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
if sys.version_info.major < 3:
    reload(sys)
sys.setdefaultencoding('utf8')



from flask import Flask
from flask_restful import Resource, Api

from gmagon.database import db
from gmagon.datainit import init as plugin_data_init
from gmagon.resources import install as plugin_resources_install

print('system-default-encoding: ' + sys.getdefaultencoding())

class System(Flask):
    """继承Flask，创建自定义类
    """

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(__name__, static_folder=None)

        self.configure()
        ##self.init_database()


    def version(self):
        return '1.0.0'

    def configure(self):
        '''
        查看帮助在线文档：http://www.pythondoc.com/flask-sqlalchemy/config.html
        '''
        self.config['BASEDIR'] = os.path.abspath(os.path.dirname(__file__))
        self.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
        # self.config['DEBUG'] = True  ## 开通Debug后，系统重启两次，这是正常的
        # self.config['HOST'] = '0.0.0.0'

    def init_database(self):
        db.init_app(self)
        with self.app_context():
            db.create_all()
            plugin_data_init()

    def run(self, host=None, port=None, debug=None, **options):
        self.init_database()
        self.configRESTFULL()
        super(self.__class__, self).run(host=host, port=port, debug=debug, **options)

    def bootstrap(self):
        """Bootstrap the system
        """

        with self.app_context():
            self.init_database()

    def configRESTFULL(self):
        api = Api(self)
        plugin_resources_install(api)
