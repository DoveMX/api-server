#!/usr/bin/env python
# -*- coding: utf-8 -*-

from api.gmagon.database import db
from model import DataTypes, Categories, Tags, Item, Set
from data import api_checkSessionAdd, api_getSpecTagItem, api_getSpecCategroyItem, api_getSpecDataTypeItem

def __getDataItem(cls=None, name='', thumb='', url='', description='', createNew=True):
    '''
    创建或者获取指定属性的数据类型Item
    :param name:
    :param description:
    :return:
    '''
    ele = cls.query.filter_by(name=name, thumb=thumb, url=url).first()
    item = None
    if ele is None:
        if createNew:
            item = cls(name=name, thumb=thumb, url=url, description=description)
            api_checkSessionAdd(item)
    else:
        item = ele

    return item




def init_test_data():
    res_item_list = __init_common_items(category_name='scene', tag_name='race', count=500)
    res_set_list = __init_common_sets(category_name='scene', tag_name='race', count=20)

    for i in range(200):
        for i_set in range(len(res_set_list)):
            res_set = res_set_list[i_set]
            res_item = res_item_list[i]
            if res_item not in res_set.items:
                res_set.items.append(res_item)
            api_checkSessionAdd(res_set)



    __init_common_items(category_name='style', tag_name='funny', count=300)


def __init_common_items(category_name='scene', tag_name='race', count=20):
    type_category = api_getSpecDataTypeItem(name='ItemCategory')
    curCategory = api_getSpecCategroyItem(name=category_name, type=type_category)
    type_tag = api_getSpecDataTypeItem(name='ItemTag')
    curTag = api_getSpecTagItem(name=tag_name, category=curCategory, type=type_tag)

    res_list = []
    for i in range(count):
        item = __getDataItem(Item, 'gif_' + str(i), thumb='https://gif' + str(i), url='https://gif' + str(i),
                             description='test')
        if curTag not in item.tags:
            item.tags.append(curTag)
        if curCategory not in item.categories:
            item.categories.append(curCategory)
        api_checkSessionAdd(item)
        res_list.append(item)

    return res_list


def __init_common_sets(category_name='scene', tag_name='race', count=10):
    type_category = api_getSpecDataTypeItem(name='SetCategory')
    curCategory = api_getSpecCategroyItem(name=category_name, type=type_category)
    type_tag = api_getSpecDataTypeItem(name='SetTag')
    curTag = api_getSpecTagItem(name=tag_name, category=curCategory, type=type_tag)

    res_list = []
    for i in range(count):
        set = __getDataItem(Set, 'gif_' + str(i), thumb='https://set' + str(i), url='https://set' + str(i),
                             description='test')
        if curTag not in set.tags:
            set.tags.append(curTag)
        if curCategory not in set.categories:
            set.categories.append(curCategory)
        api_checkSessionAdd(set)
        res_list.append(set)

    return res_list
