#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from flask_restful import Resource, reqparse

from api.gmagon.plugins.gif.util import constUriPrefix
from api.gmagon.plugins.gif.model import DataTypes, Categories, Tags, Item, Set
from api.gmagon.plugins.gif.data import api_getSpecCategroyItem, api_getSpecDataTypeItem, api_getSpecTagItem


def __installVer_1_0_0(api):
    """
    API 版本1.0.0 的接口方式定义，
    :param api:
    :return:
    """

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

    """
    通用设置
    """

    class CommonUtil:
        def __init__(self):
            pass

        @staticmethod
        def common_get_data(model, _id=None, tag_id=None, category_id=None):
            """通用方法获取数据

            """
            dataList = []

            if id is not None:
                dataItemList = model.query.filter_by(id=_id).all()
            else:
                dataItemList = model.query.filter_by().all()

            for dataItem in dataItemList:
                ele_item = dataItem.getJSON()
                dataList.append(ele_item)

            return {
                'status': 'success',
                'data': dataList,
                'count': len(dataList)
            }

        @staticmethod
        def common_get_data_ex(query, props=None):
            data_list = []
            res_list = query.all()
            if len(res_list) > 0:
                obj = res_list[0]

                for item in obj.__getattribute__(props):
                    ele_item = item.getJSON()
                    data_list.append(ele_item)

            return {
                'status': 'success',
                'data': data_list,
                'count': len(data_list)
            }

    class PaginateEnable:
        """声明统一的可分页需要的参数"""

        def __init__(self):
            self.post_parse = reqparse.RequestParser()
            self.post_parse.add_argument('page', type=int, required=True, help='No page provided', location='json')
            self.post_parse.add_argument('per_page', type=int, location='json')

        def common_post(self, query=None):
            """抽象公共的分页处理函数，针对post行为
            """
            args = self.post_parse.parse_args()

            page = args.page
            per_page = args.per_page

            data_list = []
            paginate = query.paginate(page=page, per_page=per_page, error_out=False)
            item_list = paginate.items
            if len(item_list) > 0:
                for item in item_list:
                    ele_item = item.getJSON()
                    data_list.append(ele_item)

            return {
                'status': 'success',
                'data': data_list,
                'count': len(data_list)
            }

    """
    Item相关的API资源声明
    """

    class ResItems(Resource):
        """获得所有的Item数据"""

        def get(self, item_id=None):
            return CommonUtil.common_get_data(Item, item_id)

    class ResItemsByTagId(PaginateEnable, Resource):
        """
        获取所有的Item数据通过Tag
        """

        def __init__(self):
            super(self.__class__, self).__init__()

        def get(self, tag_id):
            return CommonUtil.common_get_data_ex(Tags.query.filter_by(id=tag_id), 'items')

        def post(self, tag_id):
            """
            curl test:
            >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/items_by_tag_id/11 -d "{\"page\":1, \"per_page\":2}" -X POST -v
            """
            return self.common_post(Item.sort_items_by_tag_id(tag_id))

    class ResItemsByCategoryId(PaginateEnable, Resource):
        """
        获取所有的Item数据通过Category
        """

        def __init__(self):
            super(self.__class__, self).__init__()

        def get(self, category_id):
            return CommonUtil.common_get_data_ex(Categories.query.filter_by(id=category_id), 'items')

        def post(self, category_id):
            """
            curl test:
            >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/items_by_category_id/11 -d "{\"page\":1, \"per_page\":2}" -X POST -v
            """
            return self.common_post(Item.sort_items_by_category_id(category_id))

    class ResItemsBySetId(PaginateEnable, Resource):
        def __init__(self):
            super(self.__class__, self).__init__()

        def post(self, set_id):
            pass

    """
    Set相关的API资源声明
    """

    class ResSets(Resource):
        """
        获取资源包
        """

        def get(self, set_id=None):
            return CommonUtil.common_get_data(Set, set_id)

    class ResSetsByTagId(PaginateEnable, Resource):
        """
        获取所有资源包
        """

        def __init__(self):
            super(self.__class__, self).__init__()

        def get(self, tag_id):
            return CommonUtil.common_get_data_ex(Tags.query.filter_by(id=tag_id), 'sets')

        def post(self, tag_id):
            """
            curl test:
            >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/items_by_tag_id/11 -d "{\"page\":1, \"per_page\":2}" -X POST -v
            """
            return self.common_post(Set.sort_sets_by_tag_id(tag_id))

    class ResSetsByCategoryId(PaginateEnable, Resource):
        def __init__(self):
            super(self.__class__, self).__init__()

        def get(self, category_id):
            return CommonUtil.common_get_data_ex(Categories.query.filter_by(id=category_id), 'sets')

        def post(self, category_id):
            """
            curl test:
            >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/sets_by_category_id/11 -d "{\"page\":1, \"per_page\":2}" -X POST -v
            """
            return self.common_post(Set.sort_sets_by_category_id(category_id))

    """
    以下是API路由配置
    """
    pr = constUriPrefix + '/v1.0.0'

    api.add_resource(TestUnicode, pr + '/testunicode')

    # 基础性API获取数据接口
    api.add_resource(GetDataType, pr + '/getAllDataType')
    api.add_resource(GetDataTypeByName, pr + '/getDataType/<string:typename>')
    api.add_resource(GetAllCategoriesForItem, pr + '/getAllCategoriesForItem')
    api.add_resource(GetAllCategoriesForSet, pr + '/getAllCategoriesForSet')
    api.add_resource(GetAllCategoriesAndTagsForItem, pr + '/getAllCategoriesAndTagsForItem')
    api.add_resource(GetAllCategoriesAndTagsForSet, pr + '/getAllCategoriesAndTagsForSet')

    # Items
    api.add_resource(ResItems, pr + '/items', '/items/<int:item_id>', endpoint='items')
    api.add_resource(ResItemsByTagId, pr + '/items_by_tag_id/<int:tag_id>', endpoint='items_by_tag')
    api.add_resource(ResItemsByCategoryId, pr + '/items_by_category_id/<int:category_id>', endpoint='items_by_category')

    # Sets
    api.add_resource(ResSets, pr + '/sets', '/sets/<int:set_id>', endpoint='sets')
    api.add_resource(ResSetsByTagId, pr + '/sets_by_tag_id/<int:tag_id>', endpoint='sets_by_tag')
    api.add_resource(ResSetsByCategoryId, pr + '/sets_by_category_id/<int:category_id>', endpoint='sets_by_category')


def install(api):
    """Install for RESTFull framework"""
    __installVer_1_0_0(api)
