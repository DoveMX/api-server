#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import Resource

from api.dovemax.plugins.gif.constant import constUriPrefix

class GetDataType(Resource):
    def get(self):
        return {'status': 'success'}




def install(api):
    """Install for RESTFull framework"""
    api.add_resource(GetDataType, constUriPrefix + '/getDataType')