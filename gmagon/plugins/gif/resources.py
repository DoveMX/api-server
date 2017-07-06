#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
import types

#: lib
from flask_restful import Resource, reqparse
from sqlalchemy import util

from api.gmagon.database import db
from api.gmagon.plugins.gif.util import constUriPrefix
from api.gmagon.plugins.gif.model import DataTypes, Categories, Tags, Item, Set
from api.gmagon.plugins.gif.data import api_session_commit, api_checkSessionAdd, api_getSpecCategroyItem, \
    api_getSpecDataTypeItemById, \
    api_get_common_data_list, \
    api_get_data_with_filter_query, \
    api_getSpecDataTypeItem, api_getSpecTagItem


def __installVer_1_0_0(api):
    """
    API 版本1.0.0 的接口方式定义，
    :param api:
    :return:
    """

    pr = constUriPrefix + '/v1.0.0'

    def _get_err_info(err=''):
        return {
            'status': 'err',
            'err': err
        }

    class TestUnicode(Resource):
        def get(self):
            return {
                'status': 'success',
                'message': '中文Hello'
            }

    class BaseCURD:
        def __init__(self, cls=None):
            self.post_curd_parse = reqparse.RequestParser()
            self.post_curd_parse.add_argument('op', type=str, required=True, help='No op provided',
                                              location='json')  # 操作方式
            self.post_curd_parse.add_argument('where', type=str, required=True, help='No data provided',
                                              location='json')
            self.post_curd_parse.add_argument('data', type=dict, help='No data provided', location='json')

            self.get_curd_parse = reqparse.RequestParser()
            self.get_curd_parse.add_argument('where', type=str, required=True, help='No data provided',
                                             location='json')

            self.paginate_parse = reqparse.RequestParser()
            self.paginate_parse.add_argument('page', type=int, help='No page provided',
                                             location='json')
            self.paginate_parse.add_argument('per_page', type=int, location='json')

            self.cls = cls

        def common_curd_get(self, where=None, paginateDic=None, model_cls=None):
            """
            普通处理函数方式
            :param where:
            :param paginateDic:
            :return:
            """
            model_cls = model_cls if model_cls else self.cls
            data_list = []
            if paginateDic is not None:
                paginate = api_get_data_with_filter_query(cls=model_cls, filter=where).paginate(**paginateDic)
                item_list = paginate.items

                if len(item_list) > 0:
                    for item in item_list:
                        if isinstance(item, db.Model):
                            ele_item = item.getJSON()
                            data_list.append(ele_item)
                        else:
                            ele_item = {}
                            for i_field in range(len(item)):
                                field_ele_obj = item[i_field]
                                field_name = item._fields[i_field]
                                if isinstance(field_ele_obj, db.Model):
                                    ele_item[field_name] = field_ele_obj.getJSON()
                                else:
                                    ele_item[field_name] = field_ele_obj
                            data_list.append(ele_item)

                return {
                    'status': 'success',
                    'data': data_list,
                    'count': len(data_list),
                    'paginate': {
                        'prev_num': paginate.prev_num if paginate.prev_num is not None else 0,  # 上一页页码数
                        'next_num': paginate.next_num if paginate.next_num is not None else 0,  # 下一页页码数
                        'pages': paginate.pages,  # 总页数
                        'page': paginate.page,  # 当前页的页码(从1开始)
                        'per_page': paginate.per_page,  # 每页显示的数量
                        'total': paginate.total  # 查询返回的记录总数
                    }
                }
            else:
                data_list = api_get_data_with_filter_query(cls=model_cls, filter=where).all()
                list = []
                if len(data_list) > 0:
                    for ele in data_list:
                        list.append(ele.getJSON())

                return {
                    'status': 'success',
                    'data': list,
                    'count': len(list)
                }

        def common_curd_get_ex(self, in_where=None, usePaginate=True):
            """派生方法，自动处理where及分页"""
            where = in_where if in_where else {}
            paginate = {
                'page': 1,
                'per_page': 25
            }
            try:
                args = self.get_curd_parse.parse_args()
                where = self.__where(args)
                where = where if where else in_where

                if usePaginate:
                    paginate_args = self.paginate_parse.parse_args()
                    paginate['page'] = paginate_args.page if paginate_args.page else paginate['page']
                    paginate['per_page'] = paginate_args.per_page if paginate_args.per_page else paginate['per_page']

            except:
                if usePaginate:
                    return self.common_curd_get(where, {'page': paginate['page'],
                                                        'per_page': paginate['per_page'],
                                                        'error_out': False})
                else:
                    return self.common_curd_get(where)

        def common_curd_query(self, query, paginateDic=None):
            """通用方式查询"""
            data_list = []
            if paginateDic is not None:
                paginate = query.paginate(**paginateDic)
                item_list = paginate.items

                if len(item_list) > 0:
                    for item in item_list:
                        if isinstance(item, db.Model):
                            ele_item = item.getJSON()
                            data_list.append(ele_item)
                        else:
                            ele_item = {}
                            for i_field in range(len(item)):
                                field_ele_obj = item[i_field]
                                field_name = item._fields[i_field]
                                if isinstance(field_ele_obj, db.Model):
                                    ele_item[field_name] = field_ele_obj.getJSON()
                                else:
                                    ele_item[field_name] = field_ele_obj
                            data_list.append(ele_item)

                return {
                    'status': 'success',
                    'data': data_list,
                    'count': len(data_list),
                    'paginate': {
                        'prev_num': paginate.prev_num if paginate.prev_num is not None else 0,  # 上一页页码数
                        'next_num': paginate.next_num if paginate.next_num is not None else 0,  # 下一页页码数
                        'pages': paginate.pages,  # 总页数
                        'page': paginate.page,  # 当前页的页码(从1开始)
                        'per_page': paginate.per_page,  # 每页显示的数量
                        'total': paginate.total  # 查询返回的记录总数
                    }
                }
            else:
                data_list = query.all()
                list = []
                if len(data_list) > 0:
                    for ele in data_list:
                        list.append(ele.getJSON())

                return {
                    'status': 'success',
                    'data': list,
                    'count': len(list)
                }

        def common_curd_query_ex(self, query, usePaginate=True):
            """派生方法，自动处理where及分页"""
            paginate = {
                'page': 1,
                'per_page': 25
            }
            try:
                if usePaginate:
                    paginate_args = self.paginate_parse.parse_args()
                    paginate['page'] = paginate_args.page if paginate_args.page else paginate['page']
                    paginate['per_page'] = paginate_args.per_page if paginate_args.per_page else paginate['per_page']

            except:
                if usePaginate:
                    return self.common_curd_query(query, {'page': paginate['page'],
                                                        'per_page': paginate['per_page'],
                                                        'error_out': False})
                else:
                    return self.common_curd_query(query)

        def common_curd_post(self):
            args = self.post_curd_parse.parse_args()

            op = args.op
            data = args.data

            where = self.__where(args)

            data_item_list = None
            if re.findall('create', op):
                data_item_list = api_get_common_data_list(cls=self.cls, filter=where, update_dict=data, createNew=True)
                if len(data_item_list) > 0:
                    for sub_item in data_item_list:
                        api_checkSessionAdd(sub_item)
                api_session_commit()

            elif re.findall('update', op):
                data_item_list = api_get_common_data_list(cls=self.cls, filter=where, update_dict=data, createNew=False)
                if len(data_item_list) > 0:
                    for sub_item in data_item_list:
                        for (k, v) in data.items():
                            if hasattr(sub_item, k):
                                sub_item.__setattr__(k, v)
                        api_checkSessionAdd(sub_item)
                    api_session_commit()

            elif re.findall('delete', op):
                data_item_list = api_get_common_data_list(cls=self.cls, filter=where, createNew=False)
                if data_item_list:
                    if len(data_item_list) > 0:
                        for sub_item in data_item_list:
                            db.session.delete(sub_item)
                    api_session_commit()

            data_list = []
            if len(data_item_list):
                for ele in data_item_list:
                    data_list.append(ele.getJSON())

            return {
                'status': 'success',
                'op': op,
                'data': data_list,
                'count': len(data_list)
            }

        def __where(self, args):
            where = None
            if args is None:
                return where

            if isinstance(args.where, types.DictType):
                where = args.where
            elif args.where:
                try:
                    where = eval(args.where)
                    if not isinstance(where, types.DictType):
                        where = args.where.split(',')
                except:
                    where = args.where.split(',')
            return where

    class APIDataType(BaseCURD, Resource):
        """Table--DataType 原生处理操作"""

        def __init__(self):
            super(self.__class__, self).__init__(DataTypes)

        def get(self):
            return self.common_curd_get_ex()

        def post(self):
            return self.common_curd_post()

    class APICategories(BaseCURD, Resource):
        """Table--Categories 原生处理操作"""

        def __init__(self):
            super(self.__class__, self).__init__(Categories)

        def get(self):
            return self.common_curd_get_ex()

        def post(self):
            return self.common_curd_post()

    class APITags(BaseCURD, Resource):
        """Table--Tags 原生处理操作"""

        def __init__(self):
            super(self.__class__, self).__init__(Tags)

        def get(self):
            return self.common_curd_get_ex()

        def post(self):
            return self.common_curd_post()

    class APIItem(BaseCURD, Resource):
        """Table--Item 原生处理操作"""

        def __init__(self):
            super(self.__class__, self).__init__(Item)

        def get(self):
            return self.common_curd_get_ex()

        def post(self):
            return self.common_curd_post()

    class APISet(BaseCURD, Resource):
        """Table--Set 原生处理操作"""

        def __init__(self):
            super(self.__class__, self).__init__(Set)

        def get(self):
            return self.common_curd_get_ex()

        def post(self):
            return self.common_curd_post()

    """
    ############################################################
    """

    """
    ############################################################
    """

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
    Item相关的API资源声明
    """

    class ResItems(BaseCURD, Resource):
        """获得所有的Item数据"""

        def __init__(self):
            super(self.__class__, self).__init__(Item)

        def get(self, item_id=None):
            if item_id:
                return self.common_curd_get({'id': item_id})
            else:
                return self.common_curd_get_ex()


    class ResItemsByTagId(BaseCURD, Resource):
        """
        获取所有的Item数据通过Tag
        """
        def __init__(self):
            super(self.__class__, self).__init__(Item)

        def get(self, tag_id):
            if tag_id:
                ele = Tags.query.filter_by(id=tag_id).first()
                if ele:
                    return self.common_curd_query_ex(ele.items)
                else:
                    return _get_err_info('not found ele')
            else:
                return self.common_curd_get_ex()


    class ResItemsByCategoryId(BaseCURD, Resource):
        """
        获取所有的Item数据通过Category
        """

        def __init__(self):
            super(self.__class__, self).__init__(Item)

        def get(self, category_id):
            if category_id:
                ele = Categories.query.filter_by(id=category_id).first()
                if ele:
                    return self.common_curd_query_ex(ele.items)
                else:
                    return _get_err_info('category_id is null')
            else:
                return self.common_curd_get_ex()


    """
    Set相关的API资源声明
    """

    class ResSets(BaseCURD, Resource):
        """
        获取资源包
        """

        def __init__(self):
            super(self.__class__, self).__init__(Set)

        def get(self, set_id=None):
            if set_id:
                return self.common_curd_get({'id': set_id})
            else:
                return self.common_curd_get_ex()

    class ResSetsByTagId(BaseCURD, Resource):
        """
        获取所有资源包
        """
        def __init__(self):
            super(self.__class__, self).__init__(Set)

        def get(self, tag_id):
            if tag_id:
                ele = Tags.query.filter_by(id=tag_id).first()
                if ele:
                    return self.common_curd_query_ex(ele.sets)
                else:
                    return _get_err_info('not found ele')
            else:
                return self.common_curd_get_ex()

    class ResSetsByCategoryId(BaseCURD, Resource):
        def __init__(self):
            super(self.__class__, self).__init__(Set)

        def get(self, category_id):
            if category_id:
                ele = Categories.query.filter_by(id=category_id).first()
                if ele:
                    return self.common_curd_query_ex(ele.sets)
                else:
                    return _get_err_info('not found ele')
            else:
                return self.common_curd_get_ex()

    class ResSetItemsBySetId(BaseCURD, Resource):
        def __init__(self):
            super(self.__class__, self).__init__(Set)

        def get(self, set_id):
            if set_id:
                ele = Set.query.filter_by(id=set_id).first()
                if ele:
                    return self.common_curd_query_ex(ele.items)
                else:
                    return _get_err_info('not found ele')
            else:
                return _get_err_info('set_id is null')


    class ResSetItemsOrderBySetId(BaseCURD, Resource):
        def __init__(self):
            super(self.__class__, self).__init__(Set)

        def get(self, set_id):
            if set_id:
                ele = Set.query.filter_by(id=set_id).first()
                if ele:
                    return self.common_curd_query_ex(Set.get_items_order_by_set_id(set_id))
                else:
                    return _get_err_info('not found ele')
            else:
                return _get_err_info('set_id is null')

    """
    ############################################################
    """

    api.add_resource(TestUnicode, pr + '/testunicode')

    # types
    """
    **[GET]
    1. 无分页处理
    >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/data_type -d "{\"where\":{\"name\":\"test\"}}" -X GET -v
    1.1 单个过滤条件
    >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/data_type -d "{\"where\":\"id > 1\"}" -X GET -v
    1.2 多个过滤条件
    >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/data_type -d "{\"where\":\"id > 1, id > 4\"}" -X GET -v
    2. 有分页处理
    >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/data_type -d "{\"page\":1, \"per_page\":20, \"where\":{\"name\":\"test\"}}" -X GET -v

    **[POST]
    1. create
    >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/data_type -d "{\"op\":\"create\",\"where\":{\"name\":\"test\"},\"data\":{\"name\":\"test\",\"description\":\"testdescription\"}}" -X POST -v
    2. update
    >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/data_type -d "{\"op\":\"update\",\"where\":\"id = 9\",\"data\":{\"name\":\"test12\",\"description\":\"testdescription12\"}}" -X POST -v
    3. delete
    >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/data_type -d "{\"op\":\"delete\",\"where\":{\"id\":9}}" -X POST -v
    """
    api.add_resource(APIDataType, pr + '/data_type')

    # categories
    """
    **[GET]
    1. 无分页处理
    >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/data_categories -d "{\"where\":{\"name\":\"animal\", \"type_id\":2}}" -X GET -v
    >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/data_categories -d "{\"where\":{\"type_id\":2}}" -X GET -v
    1.1 单个过滤条件
    >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/data_categories -d "{\"where\":\"id > 5\"}" -X GET -v
    1.2 多个过滤条件
    >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/data_categories -d "{\"where\":\"id > 1, type_id = 2\"}" -X GET -v
    2. 有分页处理
    >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/data_categories -d "{\"page\":1, \"per_page\":3, \"where\":{\"type_id\":2}}" -X GET -v

    **[POST]
    参照data_type
    """
    api.add_resource(APICategories, pr + '/data_categories')

    # tags
    api.add_resource(APITags, pr + '/data_tags')

    # item
    api.add_resource(APIItem, pr + '/data_items')

    # set
    api.add_resource(APISet, pr + '/data_sets')

    ############################################
    # 获得Item所有的分类信息，不包括分类下的标签信息
    """
    ===GET
    >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/get_all_categories_for_item -X GET -v    
    """
    api.add_resource(GetAllCategoriesForItem, pr + '/get_all_categories_for_item')

    # 获得Set所有的分类信息，不包括分类下的标签信息
    """
    ===GET
    >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/get_all_categories_for_set -X GET -v 
    """
    api.add_resource(GetAllCategoriesForSet, pr + '/get_all_categories_for_set')

    # 获得Item所有的分类信息，包括分类下的标签信息
    """
    ===GET
    >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/get_all_categories_tags_for_item -X GET -v 
    """
    api.add_resource(GetAllCategoriesAndTagsForItem, pr + '/get_all_categories_tags_for_item')

    # 获得Item所有的分类信息，包括分类下的标签信息
    """
    ===GET
    >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/get_all_categories_tags_for_set -X GET -v
    """
    api.add_resource(GetAllCategoriesAndTagsForSet, pr + '/get_all_categories_tags_for_set')

    # User

    ########################################
    # Items
    """
    ===Get
    1.非分页方式
    >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/items -X GET -v
    >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/items/11 -X GET -v
    2.分页方式
    >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/items/11 -d "{\"page\":1, \"per_page\":2}" -X GET -v
    """
    api.add_resource(ResItems, pr + '/items', pr + '/items/<int:item_id>', endpoint='items')

    # 通过Tag获取信息
    """
    ===Get (支持自动分页)
    1. 
    >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/items_by_tag_id/11 -X GET -v    
    
    """
    api.add_resource(ResItemsByTagId, pr + '/items_by_tag_id/<int:tag_id>', endpoint='items_by_tag')

    # 通过Category获取信息
    """
    ===Get (支持自动分页)
    1. 
    >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/items_by_category_id/4 -X GET -v    

    """
    api.add_resource(ResItemsByCategoryId, pr + '/items_by_category_id/<int:category_id>', endpoint='items_by_category')

    ########################################
    # Sets
    api.add_resource(ResSets, pr + '/sets', '/sets/<int:set_id>', endpoint='sets')
    api.add_resource(ResSetsByTagId, pr + '/sets_by_tag_id/<int:tag_id>', endpoint='sets_by_tag')
    api.add_resource(ResSetsByCategoryId, pr + '/sets_by_category_id/<int:category_id>', endpoint='sets_by_category')
    api.add_resource(ResSetItemsBySetId, pr + '/sets_items/<int:set_id>', endpoint='sets_items')

    # 获取单个Set的元素，并包含Item的次序
    """
    ===GET
    >>> curl -i -H "Content-Type: application/json" http://127.0.0.1:5000/plugin/gif/api/v1.0.0/sets_items_order/1 -X GET -v
    """
    api.add_resource(ResSetItemsOrderBySetId, pr + '/sets_items_order/<int:set_id>', endpoint='sets_items_order')

    ########################################
    # CommentsForItem

    # CommentsForSet


    #


def install(api):
    """Install for RESTFull framework"""
    __installVer_1_0_0(api)
