#!/usr/bin/env python
# -*- coding: utf-8 -*-

from api.dovemax.common.model import retain as common_model_retain
from api.dovemax.plugins.gif.data import init_all as subsystem_gif_data_create


def init():
    common_model_retain()
    subsystem_gif_data_create()