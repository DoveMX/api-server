#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import types
#: lib
from flask_restful import Resource, reqparse

from gmagon.common.model import GUser, GUserMachines
from gmagon.database import db
from gmagon.plugins.gif.data import api_session_commit, api_checkSessionAdd, api_get_common_data_list, \
    api_get_data_with_filter_query, \
    api_getSpecDataTypeItem
from gmagon.plugins.gif.model import \
    DataTypes, Categories, Tags, Item, Set, User, tbl_set_items
from gmagon.plugins.gif.util import constUriPrefix


def _get_err_info(err=''):
    return {
        'status': 'err',
        'err': err
    }


class BaseCURD:
    def __init__(self, cls=None):
        self.post_curd_parse = reqparse.RequestParser()
        self.post_curd_parse.add_argument('op', type=str, default='query', required=True, help='No op provided',
                                          location='json')  # 操作方式
        self.post_curd_parse.add_argument('where', type=str, default='', required=True, help='No data provided',
                                          location='json')
        self.post_curd_parse.add_argument('data', type=dict, help='No data provided', location='json')

        self.get_curd_parse = reqparse.RequestParser()
        self.get_curd_parse.add_argument('where', type=str, help='No data provided',
                                         location='json')

        self.get_deep_parse = reqparse.RequestParser()
        self.get_deep_parse.add_argument('deep', type=bool, help='No data provided', location='json')

        self.paginate_parse = reqparse.RequestParser()
        self.paginate_parse.add_argument('page', type=int, help='No page provided',
                                         location='json')
        self.paginate_parse.add_argument('per_page', type=int, location='json')

        self.cls = cls

    def _get_obj_json(self, ele, deep=False):
        """
        获取有效的JSON对象
        :param ele:
        :param deep:
        :return:
        """
        json_obj = None
        if deep:
            json_obj = ele.getJSONEx()
        else:
            json_obj = ele.getJSON()

        return json_obj

    def common_curd_get(self, where=None, paginateDic=None, model_cls=None, deep=False):
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
            return self._process_data_paginate(data_list, deep, paginate)
        else:
            data_list = api_get_data_with_filter_query(cls=model_cls, filter=where).all()
            list = []
            if len(data_list) > 0:
                for ele in data_list:
                    ele_item = self._get_obj_json(ele, deep)
                    list.append(ele_item)

            return {
                'status': 'success',
                'data': list,
                'count': len(list)
            }

    def _process_data_paginate(self, data_list, deep, paginate):
        item_list = paginate.items
        if len(item_list) > 0:
            for item in item_list:
                if isinstance(item, db.Model):
                    ele_item = self._get_obj_json(item, deep)
                    data_list.append(ele_item)
                else:
                    ele_item = {}
                    for i_field in range(len(item)):
                        field_ele_obj = item[i_field]
                        field_name = item._fields[i_field]
                        if isinstance(field_ele_obj, db.Model):
                            ele_item[field_name] = self._get_obj_json(field_ele_obj, deep)
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

    def common_curd_get_ex(self, in_where=None, usePaginate=True):
        """派生方法，自动处理where及分页"""
        args_where = {}
        try:
            args = self.get_curd_parse.parse_args()
            args_where = args.where
        finally:
            pass

        where = in_where if in_where else args_where
        paginate = {
            'page': 1,
            'per_page': 25
        }
        deep = False

        print("[#] call common_curd_get_ex...")
        try:
            where = self.__where(where)
            where = where if where else {}

            deep_args = self.get_deep_parse.parse_args()
            deep = deep_args.deep

            if usePaginate:
                paginate_args = self.paginate_parse.parse_args()
                paginate['page'] = paginate_args.page if paginate_args.page else paginate['page']
                paginate['per_page'] = paginate_args.per_page if paginate_args.per_page else paginate['per_page']

                print("page=%d, per_page=%d" % (paginate['page'], paginate['per_page']))

        except Exception as e:
            print(e.message)
        finally:
            print("page=%d, per_page=%d" % (paginate['page'], paginate['per_page']))
            if usePaginate:
                return self.common_curd_get(where, {'page': paginate['page'],
                                                    'per_page': paginate['per_page'],
                                                    'error_out': False}, deep=deep)
            else:
                return self.common_curd_get(where, deep=deep)

    def common_curd_query(self, query, paginateDic=None, deep=False):
        """通用方式查询"""
        data_list = []
        if paginateDic is not None:
            paginate = query.paginate(**paginateDic)
            return self._process_data_paginate(data_list, deep, paginate)
        else:
            data_list = query.all()
            list = []
            if len(data_list) > 0:
                for ele in data_list:
                    ele_item = self._get_obj_json(ele, deep)
                    list.append(ele_item)

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

        deep = False
        try:
            deep_args = self.get_deep_parse.parse_args()
            deep = deep_args.deep

            if usePaginate:
                paginate_args = self.paginate_parse.parse_args()
                paginate['page'] = paginate_args.page if paginate_args.page else paginate['page']
                paginate['per_page'] = paginate_args.per_page if paginate_args.per_page else paginate['per_page']

                # print("page=%d, per_page=%d" % (paginate['page'], paginate['per_page']))
        finally:
            if usePaginate:
                return self.common_curd_query(query, {'page': paginate['page'],
                                                      'per_page': paginate['per_page'],
                                                      'error_out': False}, deep=deep)
            else:
                return self.common_curd_query(query, deep=deep)

    def common_curd_post(self, condition_for_query=None):
        args = self.post_curd_parse.parse_args()

        op = args.op if args.op != '' else 'query'
        data = args.data

        where = self.__where(args.where)

        data_item_list = None
        if re.findall('query', op):
            return self.common_curd_get_ex(condition_for_query)

        elif re.findall('create', op):
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

    def __where(self, in_where):
        where = None
        if in_where is None:
            return where

        if isinstance(in_where, types.DictType):
            where = in_where
        elif in_where:
            try:
                where = eval(in_where)
                if not isinstance(where, types.DictType):
                    where = in_where.split(',')
            except:
                where = in_where.split(',')
        return where


def __install_common_api_Ver_1_0_0(api):
    pr = '/api/v1.0.0'

    class APIGUser(BaseCURD, Resource):
        def __init__(self):
            super(self.__class__, self).__init__(GUser)

        def get(self):
            return self.common_curd_get_ex()

        def post(self):
            return self.common_curd_post()

    class APIGUserMachines(BaseCURD, Resource):
        def __init__(self):
            super(self.__class__, self).__init__(GUserMachines)

        def get(self):
            return self.common_curd_get_ex()

        def post(self):
            return self.common_curd_post()

    api.add_resource(APIGUser, pr + '/users', endpoint='api_g_user')

    # GUserMachines
    """
    **[GET]
    1. 无分页处理
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/api/v1.0.0/machines -d "{\"where\":{\"os\":\"MacOSX\"}}" -X GET -v
    1.1 单个过滤条件
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/api/v1.0.0/machines -d "{\"where\":\"machines.os.like(\"mac\")\"}" -X GET -vv
    2. 有分页处理
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/api/v1.0.0/machines -d "{\"page\":1, \"per_page\":20, \"where\":{\"os\":\"MacOSX\"}}" -X GET -v


    **[POST]
    1. create
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/api/v1.0.0/machines -d "{\"op\":\"create\",\"where\":{\"id\":\"NOGUserMachines\"},\"data\":{\"id\":\"NOGUserMachines\"}}" -X POST -v
    2. update
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/api/v1.0.0/machines -d "{\"op\":\"update\",\"where\":{\"id\":\"NOGUserMachines\"},\"data\":{\"os\":\"win\"}}" -X POST -v
    3. delete
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/api/v1.0.0/machines -d "{\"op\":\"delete\",\"where\":{\"id\":\"NOGUserMachines\"}}" -X POST -v
    """
    api.add_resource(APIGUserMachines, pr + '/machines', endpoint='api_g_machines')


def __install_gif_api_Ver_1_0_0(api):
    """
    API 版本1.0.0 的接口方式定义，
    :param api:
    :return:
    """

    pr = constUriPrefix + '/v1.0.0'

    class TestUnicode(Resource):
        def get(self):
            return {
                'status': 'success',
                'message': '中文Hello'
            }

    class APIUsers(BaseCURD, Resource):
        """原生处理操作"""

        def __init__(self):
            super(self.__class__, self).__init__(User)

        def get(self):
            return self.common_curd_get_ex()

        def post(self):
            return self.common_curd_post()

    class APIDataType(BaseCURD, Resource):
        """Table--DataType 原生处理操作"""

        def __init__(self):
            super(self.__class__, self).__init__(DataTypes)

        def get(self, type_id=None):
            if type_id:
                return self.common_curd_get_ex({'id': type_id})
            else:
                return self.common_curd_get_ex()

        def post(self, type_id=None):
            if type_id:
                return self.common_curd_post(condition_for_query={'id': type_id})
            else:
                return self.common_curd_post()

    class APICategories(BaseCURD, Resource):
        """Table--Categories 原生处理操作"""

        def __init__(self):
            super(self.__class__, self).__init__(Categories)

        def get(self, category_id=None):
            if category_id:
                return self.common_curd_get_ex({'id': category_id})
            else:
                return self.common_curd_get_ex()

        def post(self, category_id=None):
            if category_id:
                return self.common_curd_post(condition_for_query={'id': category_id})
            else:
                return self.common_curd_post()

    class APITags(BaseCURD, Resource):
        """Table--Tags 原生处理操作"""

        def __init__(self):
            super(self.__class__, self).__init__(Tags)

        def get(self, tag_id=None):
            if tag_id:
                return self.common_curd_get_ex({'id': tag_id})
            else:
                return self.common_curd_get_ex()

        def post(self, tag_id=None):
            if tag_id:
                return self.common_curd_post(condition_for_query={'id': tag_id})
            else:
                return self.common_curd_post()

    class APIItem(BaseCURD, Resource):
        """Table--Item 原生处理操作"""

        def __init__(self):
            super(self.__class__, self).__init__(Item)

        def get(self, item_id=None):
            if item_id:
                return self.common_curd_get_ex({'id': item_id})
            else:
                return self.common_curd_get_ex()

        def post(self, item_id=None):
            if item_id:
                return self.common_curd_post(condition_for_query={'id': item_id})
            else:
                return self.common_curd_post()

    class APISet(BaseCURD, Resource):
        """Table--Set 原生处理操作"""

        def __init__(self):
            super(self.__class__, self).__init__(Set)

        def get(self, set_id=None):
            if set_id:
                return self.common_curd_get_ex({'id': set_id})
            else:
                return self.common_curd_get_ex()

        def post(self, set_id=None):
            if set_id:
                return self.common_curd_post(condition_for_query={'id': set_id})
            else:
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

    def commonGetAllCategoriesAndTags(categoryTypeName='ItemCategory', tagTypeName='ItemTag', useJsonEx=False):
        type_item_category = api_getSpecDataTypeItem(name=categoryTypeName)
        type_item_tag = api_getSpecDataTypeItem(name=tagTypeName)

        dataList = []

        categories = Categories.query.filter_by(type=type_item_category).all()
        for cateogryObj in categories:
            ele_category = cateogryObj.getJSONEx(more=False) if useJsonEx else cateogryObj.getJSON()

            ele_category['tags'] = []
            tags = cateogryObj.tags
            for tagObj in tags:
                ele_category['tags'].append(tagObj.getJSONEx(more=False) if useJsonEx else tagObj.getJSON())

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
            return commonGetAllCategoriesAndTags('ItemCategory', 'ItemTag', useJsonEx=True)

    class GetAllCategoriesAndTagsForSet(Resource):
        """获取Set所有分类及分类下标签结构"""

        def get(self):
            return commonGetAllCategoriesAndTags('SetCategory', 'SetTag', useJsonEx=True)

    """
    User 用户部分
    """

    class ResUsers(BaseCURD, Resource):
        def __init__(self):
            super(self.__class__, self).__init__(User)

        def get(self, user_id=None):
            if user_id:
                return self.common_curd_get({'id': user_id})
            else:
                return self.common_curd_get_ex()

    """
    Item相关的API资源声明
    """

    class ResItems(BaseCURD, Resource):
        """获得所有的Item数据"""

        def __init__(self):
            super(self.__class__, self).__init__(Item)

        def get(self, item_id=None):
            if item_id:
                return self.common_curd_get_ex({'id': item_id})
            else:
                return self.common_curd_get_ex()

        def post(self, item_id=None):
            return self.get(item_id)

    class ResItemsByTagId(BaseCURD, Resource):
        """
        获取所有的Item数据通过Tag
        """

        def __init__(self):
            super(self.__class__, self).__init__(Item)

        def _get_post(self, tag_id=None):
            if tag_id:
                ele = Tags.query.filter_by(id=tag_id).first()
                if ele:
                    return self.common_curd_query_ex(ele.items)
                else:
                    return _get_err_info('not found ele')
            else:
                return self.common_curd_get_ex()

        def get(self, tag_id=None):
            return self._get_post(tag_id)

        def post(self, tag_id=None):
            # json_data = flask_request.get_json(force=True)
            # print("json_data=%s" % (json_data['page']))
            return self._get_post(tag_id)

    class ResItemsByCategoryId(BaseCURD, Resource):
        """
        获取所有的Item数据通过Category
        """

        def __init__(self):
            super(self.__class__, self).__init__(Item)

        def get(self, category_id=None):
            if category_id:
                ele = Categories.query.filter_by(id=category_id).first()
                if ele:
                    return self.common_curd_query_ex(ele.items)
                else:
                    return _get_err_info('category_id is null')
            else:
                return self.common_curd_get_ex()

        def post(self, category_id=None):
            return self.get(category_id)

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

        def post(self, set_id=None):
            return self.get(set_id)

    class ResSetsByTagId(BaseCURD, Resource):
        """
        获取所有资源包
        """

        def __init__(self):
            super(self.__class__, self).__init__(Set)

        def get(self, tag_id=None):
            if tag_id:
                ele = Tags.query.filter_by(id=tag_id).first()
                if ele:
                    return self.common_curd_query_ex(ele.sets)
                else:
                    return _get_err_info('not found ele')
            else:
                return self.common_curd_get_ex()

        def post(self, tag_id=None):
            return self.get(tag_id)

    class ResSetsByCategoryId(BaseCURD, Resource):
        def __init__(self):
            super(self.__class__, self).__init__(Set)

        def get(self, category_id=None):
            if category_id:
                ele = Categories.query.filter_by(id=category_id).first()
                if ele:
                    return self.common_curd_query_ex(ele.sets)
                else:
                    return _get_err_info('not found ele')
            else:
                return self.common_curd_get_ex()

        def post(self, category_id=None):
            return self.get(category_id)

    class ResSetItemsBySetId(BaseCURD, Resource):
        def __init__(self):
            super(self.__class__, self).__init__(Set)

        def get(self, set_id=None):
            if set_id:
                ele = Set.query.filter_by(id=set_id).first()
                if ele:
                    return self.common_curd_query_ex(ele.items)
                else:
                    return _get_err_info('not found ele')
            else:
                return _get_err_info('set_id is null')

        def post(self, set_id=None):
            return self.get(set_id)

    class ResSetItemsOrderBySetId(BaseCURD, Resource):
        def __init__(self):
            super(self.__class__, self).__init__(Set)

        def get(self, set_id=None):
            if set_id:
                ele = Set.query.filter_by(id=set_id).first()
                if ele:
                    return self.common_curd_query_ex(Set.get_items_order_by_set_id(set_id))
                else:
                    return _get_err_info('not found ele')
            else:
                return _get_err_info('set_id is null')

        def post(self, set_id=None):
            return self.get(set_id)

    class ManagerSetItems(BaseCURD, Resource):
        """
        管理Set集合中的Item数据
        """
        def __init__(self):
            super(self.__class__, self).__init__(tbl_set_items.c)

        def post(self):
            return self.common_curd_post()

    """
    ############################################################
    """

    class ResRelationData(Resource):
        def __init__(self, props=None, cls=None, ref_cls=None):
            self.props = props
            self.cls = cls
            self.refCls = ref_cls
            self.post_args = reqparse.RequestParser()

            self.post_args.add_argument('op', type=str, required=True, help='No op provided',
                                        location='json')
            self.post_args.add_argument('where', type=str, required=True, help='find in refCLS',
                                        location='json')
            self.post_args.add_argument('filter', type=str, help='find in cls', location='json')

        def __where(self, in_where):
            where = None
            if in_where is None:
                return where

            if isinstance(in_where, types.DictType):
                where = in_where
            elif in_where:
                try:
                    where = eval(in_where)
                    if not isinstance(where, types.DictType):
                        where = in_where.split(',')
                except:
                    where = in_where.split(',')
            return where

        def post(self):
            try:
                args = self.post_args.parse_args()

                # 查找相关的类型的数据有多少
                where = self.__where(args.where)
                ref_data_list = api_get_data_with_filter_query(cls=self.refCls, filter=where).all()

                # 查找符合filter过滤条件的对象
                filter = self.__where(args.filter)
                data_list = api_get_data_with_filter_query(cls=self.cls, filter=filter).all()

                # 开始处理
                for ele in data_list:
                    for ref_ele in ref_data_list:
                        query = ele.__getattribute__(self.props)
                        if query:
                            query.append(ref_ele)

                return {
                    'status': 'success'
                }

            except Exception as e:
                return _get_err_info(e.message)

    class ResItemTagsData(ResRelationData):
        def __init__(self):
            super(self.__class__, self).__init__(props='tags', cls=Item, ref_cls=Tags)

    class ResItemCategoriesData(ResRelationData):
        def __init__(self):
            super(self.__class__, self).__init__(props='categories', cls=Item, ref_cls=Categories)

    class ResSetTagsData(ResRelationData):
        def __init__(self):
            super(self.__class__, self).__init__(props='tags', cls=Set, ref_cls=Tags)

    class ResSetCategoriesData(ResRelationData):
        def __init__(self):
            super(self.__class__, self).__init__(props='categories', cls=Set, ref_cls=Categories)

    """
    ############################################################
    """

    class ResTraceUserData(Resource):
        def __init__(self, props=None, cls=None):
            self.props = props
            self.cls = cls
            self.post_args = reqparse.RequestParser()
            self.post_args.add_argument('machine_id', type=str, required=True, help='No machine_id provided',
                                        location='json')
            self.post_args.add_argument('id', type=int, required=True, help='No id provided',
                                        location='json')

        def post(self):
            try:
                args = self.post_args.parse_args()

                user = User.query.filter_by(machine_id=args.machine_id).first()
                item = self.cls.query.filter_by(id=args.id).first()

                if user and item:
                    query = item.__getattribute__(self.props)
                    if query:
                        query.append(user)
                        return {
                            'status': 'success'
                        }
                    else:
                        raise Exception('no query obj')
                else:
                    raise Exception('no found user or item')


            except Exception as e:
                return _get_err_info(e.message)

    class ResItemDownloadUser(ResTraceUserData):
        def __init__(self):
            super(self.__class__, self).__init__(props='download_users', cls=Item)

    class ResItemPreviewUser(ResTraceUserData):
        def __init__(self):
            super(self.__class__, self).__init__(props='preview_users', cls=Item)

    class ResItemCollectionUser(ResTraceUserData):
        def __init__(self):
            super(self.__class__, self).__init__(props='collection_users', cls=Item)

    class ResItemShareUser(ResTraceUserData):
        def __init__(self):
            super(self.__class__, self).__init__(props='share_users', cls=Item)

    class ResSetDownloadUser(ResTraceUserData):
        def __init__(self):
            super(self.__class__, self).__init__(props='download_users', cls=Set)

    class ResSetPreviewUser(ResTraceUserData):
        def __init__(self):
            super(self.__class__, self).__init__(props='preview_users', cls=Set)

    class ResSetCollectionUser(ResTraceUserData):
        def __init__(self):
            super(self.__class__, self).__init__(props='collection_users', cls=Set)

    class ResSetShareUser(ResTraceUserData):
        def __init__(self):
            super(self.__class__, self).__init__(props='share_users', cls=Set)

    api.add_resource(TestUnicode, pr + '/testunicode')

    # users
    """
    **[GET]
    1. 无分页处理
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/data_user -d "{\"where\":{\"machine_id\":\"NOGUserMachines\"}}" -X GET -v
    
    **[POST]
    1. create
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/data_user -d "{\"op\":\"create\",\"where\":{\"machine_id\":\"NOGUserMachines\"},\"data\":{\"machine_id\":\"NOGUserMachines\"}}" -X POST -v
    2. update
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/data_user -d "{\"op\":\"update\",\"where\":{\"machine_id\":\"NOGUserMachines\"},\"data\":{\"machine_id\":\"NOGUserMachines\"}}" -X POST -v
    3. delete
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/data_user -d "{\"op\":\"delete\",\"where\":{\"machine_id\":\"NOGUserMachines\"}}" -X POST -v
    """
    api.add_resource(APIUsers, pr + '/data_user', endpoint='gif_users')

    # types
    """
    **[GET]
    1. 无分页处理
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/data_type -d "{\"where\":{\"name\":\"test\"}}" -X GET -v
    1.1 单个过滤条件
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/data_type -d "{\"where\":\"id > 1\"}" -X GET -v
    1.2 多个过滤条件
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/data_type -d "{\"where\":\"id > 1, id > 4\"}" -X GET -v
    2. 有分页处理
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/data_type -d "{\"page\":1, \"per_page\":20, \"where\":{\"name\":\"test\"}}" -X GET -v

    **[POST]
    1. create
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/data_type -d "{\"op\":\"create\",\"where\":{\"name\":\"test\"},\"data\":{\"name\":\"test\",\"description\":\"testdescription\"}}" -X POST -v
    2. update
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/data_type -d "{\"op\":\"update\",\"where\":\"id = 9\",\"data\":{\"name\":\"test12\",\"description\":\"testdescription12\"}}" -X POST -v
    3. delete
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/data_type -d "{\"op\":\"delete\",\"where\":{\"id\":9}}" -X POST -v
    """
    api.add_resource(APIDataType, pr + '/data_type', pr + '/data_type/<int:type_id>')

    # categories
    """
    **[GET]
    1. 无分页处理
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/data_categories -d "{\"where\":{\"name\":\"animal\", \"type_id\":2}}" -X GET -v
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/data_categories -d "{\"where\":{\"type_id\":2}}" -X GET -v
    1.1 单个过滤条件
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/data_categories -d "{\"where\":\"id > 5\"}" -X GET -v
    1.2 多个过滤条件
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/data_categories -d "{\"where\":\"id > 1, type_id = 2\"}" -X GET -v
    2. 有分页处理
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/data_categories -d "{\"page\":1, \"per_page\":3, \"where\":{\"type_id\":2}}" -X GET -v

    **[POST]
    参照data_type
    """
    api.add_resource(APICategories, pr + '/data_categories', pr + '/data_categories/<int:category_id>')

    # tags
    api.add_resource(APITags, pr + '/data_tags', pr + '/data_tags/<int:tag_id>')

    # item
    api.add_resource(APIItem, pr + '/data_items', pr + '/data_items/<int:item_id>')

    # set
    api.add_resource(APISet, pr + '/data_sets', pr + '/data_sets/<int:set_id>')

    ############################################
    # 获得Item所有的分类信息，不包括分类下的标签信息
    """
    ===GET
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/get_all_categories_for_item -X GET -v    
    """
    api.add_resource(GetAllCategoriesForItem, pr + '/get_all_categories_for_item')

    # 获得Set所有的分类信息，不包括分类下的标签信息
    """
    ===GET
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/get_all_categories_for_set -X GET -v 
    """
    api.add_resource(GetAllCategoriesForSet, pr + '/get_all_categories_for_set')

    # 获得Item所有的分类信息，包括分类下的标签信息
    """
    ===GET
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/get_all_categories_tags_for_item -X GET -v 
    """
    api.add_resource(GetAllCategoriesAndTagsForItem, pr + '/get_all_categories_tags_for_item')

    # 获得Set所有的分类信息，包括分类下的标签信息
    """
    ===GET
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/get_all_categories_tags_for_set -X GET -v
    """
    api.add_resource(GetAllCategoriesAndTagsForSet, pr + '/get_all_categories_tags_for_set')

    # User

    ########################################
    # Items
    """
    ===Get
    1.非分页方式
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/items -X GET -v
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/items/11 -X GET -v
    2.分页方式
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/items/11 -d "{\"page\":1, \"per_page\":2}" -X GET -v
    """
    api.add_resource(ResItems, pr + '/items', pr + '/items/<int:item_id>', endpoint='items')

    # 通过Tag获取信息
    """
    ===Get (支持自动分页)
    1. 
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/items_by_tag_id/11 -X GET -v    
    
    """
    api.add_resource(ResItemsByTagId, pr + '/items_by_tag_id/<int:tag_id>', endpoint='items_by_tag')

    # 通过Category获取信息
    """
    ===Get (支持自动分页)
    1. 
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/items_by_category_id/4 -X GET -v    

    """
    api.add_resource(ResItemsByCategoryId, pr + '/items_by_category_id/<int:category_id>', endpoint='items_by_category')

    # 记录以下数据
    """只支持POST方式
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/items_download -d "{\"machine_id\":\"NOGUserMachines\", \"item_id\":1}" -X POST -v
    """
    api.add_resource(ResItemDownloadUser, pr + '/items_download', endpoint='items_download')
    api.add_resource(ResItemPreviewUser, pr + '/items_preview', endpoint='items_preview')
    api.add_resource(ResItemCollectionUser, pr + '/items_collection', endpoint='items_collection')
    api.add_resource(ResItemShareUser, pr + '/items_share', endpoint='items_share')

    # 操作Item所属分类及标签的处理
    api.add_resource(ResItemTagsData, pr + '/items_tags_data', endpoint='items_tags_data')
    api.add_resource(ResItemCategoriesData, pr + '/items_categories_data', endpoint='items_categories_data')

    ########################################
    # Sets
    """
    ===Get
    1.非分页方式
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/sets -X GET -v
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/sets/1 -X GET -v
    2.分页方式
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/sets/1 -d "{\"page\":1, \"per_page\":2}" -X GET -v
    """
    api.add_resource(ResSets, pr + '/sets', '/sets/<int:set_id>', endpoint='sets')
    api.add_resource(ResSetsByTagId, pr + '/sets_by_tag_id/<int:tag_id>', endpoint='sets_by_tag')
    api.add_resource(ResSetsByCategoryId, pr + '/sets_by_category_id/<int:category_id>', endpoint='sets_by_category')
    api.add_resource(ResSetItemsBySetId, pr + '/sets_items/<int:set_id>', endpoint='sets_items')

    # 获取单个Set的元素，并包含Item的次序
    """
    ===GET
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/sets_items_order/1 -X GET -v
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/sets_items_order/1 -d "{\"deep\":1}" -X GET -v
    """
    api.add_resource(ResSetItemsOrderBySetId, pr + '/sets_items_order/<int:set_id>', endpoint='sets_items_order')


    # 管理单个Set中的Item
    """
    ===POST
    >>> curl -i -H "Content-Type: application/json" 
        http://192.168.3.6:5000/plugin/gif/api/v1.0.0/mgr_data_sets_items 
        -d "{\"op\":\"create\",\"where\":{\"set_id\":1, \"item_id\": 11},\"data\":{\"set_id\":1, \"item_id\": 11, \"order\": 1, \"bewrite\":\"Test\"}}"
        -X POST -v
    
    """
    api.add_resource(ManagerSetItems, pr + '/mgr_data_sets_items', endpoint='mgr_data_sets_items')

    # 记录以下数据
    """只支持POST方式
    >>> curl -i -H "Content-Type: application/json" http://192.168.3.6:5000/plugin/gif/api/v1.0.0/sets_download -d "{\"machine_id\":\"NOGUserMachines\", \"item_id\":1}" -X POST -v
    """
    api.add_resource(ResSetDownloadUser, pr + '/sets_download', endpoint='sets_download')
    api.add_resource(ResSetPreviewUser, pr + '/sets_preview', endpoint='sets_preview')
    api.add_resource(ResSetCollectionUser, pr + '/sets_collection', endpoint='sets_collection')
    api.add_resource(ResSetShareUser, pr + '/sets_share', endpoint='sets_share')

    # 操作Item所属分类及标签的处理
    api.add_resource(ResSetTagsData, pr + '/sets_tags_data', endpoint='sets_tags_data')
    api.add_resource(ResSetCategoriesData, pr + '/sets_categories_data', endpoint='sets_categories_data')


    ########################################
    # CommentsForItem

    # CommentsForSet


    #


def install(api):
    """Install for RESTFull framework"""
    __install_common_api_Ver_1_0_0(api)
    __install_gif_api_Ver_1_0_0(api)
