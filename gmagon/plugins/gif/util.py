#!/usr/bin/env python
# -*- coding: utf-8 -*-

constTablePrefix = 'gif_$_' ## 定义表的前缀
constSchema = 'gif' ## 定义Schema
constUriPrefix = '/plugin/gif/api'

def format_datetime(datetime):
    return datetime.strftime( '%Y-%m-%d %H:%M:%S %f' )