#!/usr/bin/env python
# -*- coding: utf-8 -*-

from api.gmagon.database import db
from model import DataTypes, Categories, Tags, Item
from data import api_checkSessionAdd, api_getSpecTagItem, api_getSpecCategroyItem, api_getSpecDataTypeItem

def __getDataItem(cls=None, name='', thumb='', url='', description='', createNew=True):
    '''
    创建或者获取指定属性的数据类型Item
    :param name:
    :param description:
    :return:
    '''
    ele_list = cls.query.filter_by(name=name, thumb=thumb, url=url).all()
    item = None
    if len(ele_list) < 1:
        if createNew:
            item = cls(name=name, thumb=thumb, url=url, description=description)
            api_checkSessionAdd(item)
    else:
        item = ele_list[0]

    return item




def init_test_data():
    __init_scene_race_items()
    __init_style_funny_items()


def __init_scene_race_items():
    type_item_category = api_getSpecDataTypeItem(name='ItemCategory')
    curCategory = api_getSpecCategroyItem(name='scene', type=type_item_category)
    type_item_tag = api_getSpecDataTypeItem(name='ItemTag')
    curTag = api_getSpecTagItem(name='race', category=curCategory, type=type_item_tag)
    for i in range(10):
        item = __getDataItem(Item, 'gif_' + str(i), thumb='https://gif' + str(i), url='https://gif' + str(i),
                             description='test')
        if curTag not in item.tags:
            item.tags.append(curTag)
        if curCategory not in item.categories:
            item.categories.append(curCategory)
        api_checkSessionAdd(item)

def __init_style_funny_items():
    type_item_category = api_getSpecDataTypeItem(name='ItemCategory')
    curCategory = api_getSpecCategroyItem(name='style', type=type_item_category)
    type_item_tag = api_getSpecDataTypeItem(name='ItemTag')
    curTag = api_getSpecTagItem(name='funny', category=curCategory, type=type_item_tag)
    for i in range(4):
        item = __getDataItem(Item, 'gif_' + str(i), thumb='https://gif' + str(i), url='https://gif' + str(i),
                             description='test')
        if curTag not in item.tags:
            item.tags.append(curTag)
        if curCategory not in item.categories:
            item.categories.append(curCategory)
        api_checkSessionAdd(item)