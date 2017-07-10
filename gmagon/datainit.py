#!/usr/bin/env python
# -*- coding: utf-8 -*-

#: lib
from flask_restful import Resource, reqparse

#: local
from gmagon.common.model import retain as common_model_retain
from gmagon.plugins.gif.data import init_all as subsystem_gif_data_create


def init(api):
    common_model_retain()

    class InitSubSystemGifData(Resource):
        def get(self):
            subsystem_gif_data_create()
            return {
                'state': 'success'
            }

    """
    http://127.0.0.1:5000/gif/data_init
    """
    api.add_resource(InitSubSystemGifData, '/gif/data_init')
