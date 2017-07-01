#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from flask_restful import Resource


from api.gmagon.plugins.gif.util import constUriPrefix
from api.gmagon.plugins.gif.model import DataTypes, Categories, Tags, Item
from api.gmagon.plugins.gif.data import api_getSpecCategroyItem, api_getSpecDataTypeItem, api_getSpecTagItem


class TestUnicode(Resource):
    def get(self):
        return {
            'status': 'success',
            'message': '中文Hello'
        }


class GetDataType(Resource):
    def get(self):
        dataList = DataTypes.query.filter_by().all()
        list = []

        if len(dataList) > 0:
            for ele in dataList:
                list.append(ele.getJSON())

        return {
            'status': 'success',
            'list': list,
            'count': len(list)
        }

class GetDataTypeByName(Resource):
    def get(self, typename):
        dataList = DataTypes.query.filter_by(name=typename).all()
        list = []

        if len(dataList) > 0:
            for ele in dataList:
                list.append(ele.getJSON())

        return {
            'status': 'success',
            'list': list,
            'count': len(list)
        }

def commonGetCategories(dataTypeName=''):
    type_item_category = api_getSpecDataTypeItem(name=dataTypeName)
    dataList = Categories.query.filter_by(type=type_item_category).all()
    list = []

    if len(dataList) > 0:
        for ele in dataList:
            list.append(ele.getJSON())

    return {
        'status': 'success',
        'list': list,
        'count': len(list)
    }

def commonGetAllCategoriesAndTags(categoryTypeName='ItemCategory', tagTypeName='ItemTag'):
    type_item_category = api_getSpecDataTypeItem(name=categoryTypeName)
    type_item_tag = api_getSpecDataTypeItem(name=tagTypeName)

    dataList = []

    categories = Categories.query.filter_by(type=type_item_category).all()
    for cateogryObj in categories:
        ele_category = cateogryObj.getJSON()

        ele_category['tags'] = []
        tags = cateogryObj.tags
        for tagObj in tags:
            ele_category['tags'].append(tagObj.getJSON())

        dataList.append(ele_category)

    return {
        'status': 'success',
        'data': dataList
    }


class GetAllCategoriesForItem(Resource):
    """获得Item有哪些分类"""
    def get(self):
        return commonGetCategories('ItemCategory')

class GetAllCategoriesForSet(Resource):
    """获得Set有哪些分类"""
    def get(self):
        return commonGetCategories('SetCategory')

class GetAllCategoriesAndTagsForItem(Resource):
    """获取Item所有分类及分类下标签结构"""
    def get(self):
        return commonGetAllCategoriesAndTags('ItemCategory', 'ItemTag')

class GetAllCategoriesAndTagsForSet(Resource):
    """获取Set所有分类及分类下标签结构"""
    def get(self):
        return commonGetAllCategoriesAndTags('SetCategory', 'SetTag')

class GetAllItems(Resource):
    """获得所有的Item数据"""
    def get(self):
        dataList = []

        items = Item.query.filter_by().all()
        for item in items:
            ele_item = item.getJSON()
            dataList.append(ele_item)

        return {
            'status': 'success',
            'data': dataList
        }

def install(api):
    """Install for RESTFull framework"""
    api.add_resource(TestUnicode, constUriPrefix + '/v1.0.0/testunicode')

    ## 基础性API获取数据接口
    api.add_resource(GetDataType, constUriPrefix + '/v1.0.0/getAllDataType')
    api.add_resource(GetDataTypeByName, constUriPrefix + '/v1.0.0/getDataType/<string:typename>')
    api.add_resource(GetAllCategoriesForItem, constUriPrefix + '/v1.0.0/getAllCategoriesForItem')
    api.add_resource(GetAllCategoriesForSet, constUriPrefix + '/v1.0.0/getAllCategoriesForSet')
    api.add_resource(GetAllCategoriesAndTagsForItem, constUriPrefix + '/v1.0.0/getAllCategoriesAndTagsForItem')
    api.add_resource(GetAllCategoriesAndTagsForSet, constUriPrefix + '/v1.0.0/getAllCategoriesAndTagsForSet')
    api.add_resource(GetAllItems, constUriPrefix + '/v1.0.0/getAllItems')