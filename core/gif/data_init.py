#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..database import db
from orm_def import DataTypes, Categories, Tags


def __checkSessionAdd(data_item):
    if data_item:
        db.session.add(data_item)

def __getSpecDataTypeItem(name, description):
    '''
    创建或者获取指定属性的数据类型Item
    :param name:
    :param description:
    :return:
    '''
    ele_list = DataTypes.query.filter_by(name=name).all()
    item = None
    if len(ele_list) < 1:
        item = DataTypes(name=name, description=description)
        __checkSessionAdd(item)
    else:
        item = ele_list[0]

    return item

def __getSpecCategroyItem(name, description, type, parent=None):
    '''
    创建或者获取指定属性的分类Item
    :param name:
    :param description:
    :param type:
    :param parent:
    :return:
    '''
    ele_list = []
    if parent:
        ele_list = Categories.query.filter_by(name=name, type_id=type.id, parent_id=parent.id).all()
    else:
        ele_list = Categories.query.filter_by(name=name, type_id=type.id).all()

    item = None
    if len(ele_list) < 1:
        if parent:
            item = Categories(name=name, description=description, type=type, parent=parent)
        else:
            item = Categories(name=name, description=description, type=type)
        __checkSessionAdd(item)
    else:
        item = ele_list[0]

    return item

def __getSpecTagItem(name, description, category, type):
    '''
    创建或者获取指定属性的标签Item
    :param name:
    :param description:
    :param category:
    :param type:
    :return:
    '''
    ele_list = Tags.query.filter_by(name=name, description=description, type=type, category=category).all()
    if len(ele_list) < 1:
        item = Tags(name=name, description=description, type=type, category=category)
        __checkSessionAdd(item)
    else:
        item = ele_list[0]

    return item


def __init_data_for_item(type_item_category, type_item_tag):
    '''
    参照网易云音乐对歌单的标签分类 {Item}
    :param type_item_category:
    :param type_item_tag:
    :return:
    '''
    curCategory = __getSpecCategroyItem(name='animal', description='动物', type=type_item_category)
    __getSpecTagItem(name='dog', description='狗', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='cat', description='猫', category=curCategory, type=type_item_tag)


    curCategory = __getSpecCategroyItem(name='traffic', description='交通', type=type_item_category)
    curCategory = __getSpecCategroyItem(name='style', description='风格', type=type_item_category)
    curCategory = __getSpecCategroyItem(name='scene', description='场景', type=type_item_category)
    curCategory = __getSpecCategroyItem(name='subject', description='主题', type=type_item_category)
    curCategory = __getSpecCategroyItem(name='emotion', description='情感', type=type_item_category)



def __init_data_for_set(type_item_category, type_item_tag):
    '''
    参照网易云音乐对歌单的标签分类 {Set}
    :param type_item_category:
    :param type_item_tag:
    :return:
    '''
    curCategory = __getSpecCategroyItem(name='animal', description='动物', type=type_item_category)
    __getSpecTagItem(name='dog', description='狗', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='cat', description='猫', category=curCategory, type=type_item_tag)


    curCategory = __getSpecCategroyItem(name='traffic', description='交通', type=type_item_category)
    curCategory = __getSpecCategroyItem(name='style', description='风格', type=type_item_category)
    curCategory = __getSpecCategroyItem(name='scene', description='场景', type=type_item_category)
    curCategory = __getSpecCategroyItem(name='subject', description='主题', type=type_item_category)
    curCategory = __getSpecCategroyItem(name='emotion', description='情感', type=type_item_category)


def init_all():
    '''
    初始化原始数据
    :return:
    '''
    print('call one ...')


    type_data = __getSpecDataTypeItem(name='Data', description='基础的数据类型')
    type_item_category = __getSpecDataTypeItem(name='ItemCategory', description='Item分类的类型')
    type_set_category = __getSpecDataTypeItem(name='SetCategory', description='Set分类的类型')
    type_item_tag = __getSpecDataTypeItem(name='ItemTag', description='Item标签的类型')
    type_set_tag = __getSpecDataTypeItem(name='SetTag', description='Set标签的类型')
    type_user_analysis = __getSpecDataTypeItem(name='AnalysisType', description='分析数据类型')

    __init_data_for_item(type_item_category, type_item_tag)
    __init_data_for_set(type_set_category, type_set_tag)

    db.session.commit()