#!/usr/bin/env python
# -*- coding: utf-8 -*-

from api.dovemax.plugins.gif.resources import install as plugin_gif_resources_install

def install(api=None):
    """Install for RESTFull framework"""
    plugin_gif_resources_install(api)