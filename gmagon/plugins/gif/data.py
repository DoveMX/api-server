#!/usr/bin/env python
# -*- coding: utf-8 -*-

# system
import types

# local
from api.gmagon.database import db
from api.gmagon.plugins.gif.model import DataTypes, Categories, Tags


def __checkSessionAdd(data_item):
    if data_item:
        db.session.add(data_item)


def __get_data_with_filter(cls, filter={}, update_dict={}, createNew=True):
    ele = None
    if isinstance(filter, types.DictType):
        ele = cls.query.filter_by(**filter).first()
    else:
        ele = cls.query.filter(*filter).first()

    item = None
    if ele is None:
        if createNew:
            item = cls(**update_dict)
            __checkSessionAdd(item)
    else:
        item = ele

    return item

def __get_data_with_filter_list(cls, filter={}, update_dict={}, createNew=True):
    ele_list = []
    if isinstance(filter, types.DictType):
        ele_list = cls.query.filter_by(**filter).all()
    else:
        ele_list = cls.query.filter(*filter).all()

    if len(ele_list) == 0:
        if createNew:
            item = cls(**update_dict)
            __checkSessionAdd(item)
            ele_list.append(item)

    return ele_list


def __get_data_with_filter_query(cls=None, filter=None):
    query = None
    if isinstance(filter, types.DictType):
        query = cls.query.filter_by(**filter)
    elif isinstance(filter, types.ListType):
        query = cls.query.filter(*filter)

    if query:
        print  "SQL: %s\n" % str(query.statement)

    return query




def __getSpecDataTypeItem(name, description='', createNew=True):
    return __get_data_with_filter(cls=DataTypes, filter={'name': name},
                                  update_dict={'name': name, 'description': description}, createNew=createNew)


def __getSpecCategroyItem(name, description='', type=None, parent=None, createNew=True):
    '''
    创建或者获取指定属性的分类Item=
    :param name:
    :param description:
    :param type:
    :param parent:
    :return:
    '''
    ele = None
    if parent:
        ele = Categories.query.filter_by(name=name, type_id=type.id, parent_id=parent.id).first()
    else:
        ele = Categories.query.filter_by(name=name, type_id=type.id).first()

    item = None
    if ele is None:
        if createNew:
            if parent:
                item = Categories(name=name, description=description, type=type, parent=parent)
            else:
                item = Categories(name=name, description=description, type=type)
            __checkSessionAdd(item)
    else:
        item = ele

    return item


def __getSpecTagItem(name, description='', category=None, type=None, createNew=True):
    '''
    创建或者获取指定属性的标签Item
    :param name:
    :param description:
    :param category:
    :param type:
    :return:
    '''
    item = None
    ele = Tags.query.filter_by(name=name, type=type, category=category).first()
    if ele is None:
        if createNew:
            item = Tags(name=name, description=description, type=type, category=category)
            __checkSessionAdd(item)
    else:
        item = ele

    return item


def __initDataForItemAndSetCommon(type_item_category, type_item_tag):
    '''
    参照网易云音乐对歌单的标签分类 {Item}, 参照网易云音乐对歌单的标签分类 {Set}
    :param type_item_category:
    :param type_item_tag:
    :return:
    '''

    '''
    与动物有关的
    '''
    curCategory = __getSpecCategroyItem(name='animal', description='动物', type=type_item_category)
    __getSpecTagItem(name='dog', description='狗', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='cat', description='猫', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='mouse', description='老鼠', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='horse', description='马', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='kangaroo', description='袋鼠', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='chicken', description='鸡', category=curCategory, type=type_item_tag)

    '''
    与科技相关
    '''
    curCategory = __getSpecCategroyItem(name='technology', description='科技', type=type_item_category)
    __getSpecTagItem(name='robot', description='机器人', category=curCategory, type=type_item_tag)

    '''
    与交通有关的
    '''
    curCategory = __getSpecCategroyItem(name='traffic', description='交通', type=type_item_category)
    __getSpecTagItem(name='cat', description='小汽车', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='bus', description='公交车', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='bike', description='自行车', category=curCategory, type=type_item_tag)

    '''
    让你感觉是有什么特别的
    '''
    curCategory = __getSpecCategroyItem(name='style', description='风格', type=type_item_category)
    __getSpecTagItem(name='funny', description='搞笑', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='retch', description='恶心', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='boredom', description='无聊', category=curCategory, type=type_item_tag)

    '''
    展现内容，与当时出现的天气有关
    '''
    curCategory = __getSpecCategroyItem(name='weather', description='气象', type=type_item_category)
    __getSpecTagItem(name='heavy-rain', description='暴雨', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='typhoon', description='台风', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='tornado', description='龙卷风', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='hail', description='冰雹', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='snowstorm', description='暴风雪', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='high-temperature', description='高温', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='cold', description='寒冷', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='extremely-cold', description='极寒', category=curCategory, type=type_item_tag)

    '''
    展现内容，当时出现的场景主要状态
    '''
    curCategory = __getSpecCategroyItem(name='scene', description='场景', type=type_item_category)
    __getSpecTagItem(name='drive', description='驾车', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='sport', description='运动', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='race', description='比赛', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='work', description='工作', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='study', description='学习', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='rest', description='休息', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='travel', description='旅行', category=curCategory, type=type_item_tag)

    '''
    能让你感觉到什么，这是情感
    '''
    curCategory = __getSpecCategroyItem(name='emotion', description='情感', type=type_item_category)
    __getSpecTagItem(name='nostalgic', description='怀旧', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='fresh', description='清新', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='romantic', description='浪漫', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='sexy', description='性感', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='sad', description='伤感', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='angry', description='生气', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='cure', description='治愈', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='relax', description='放松', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='lonely', description='孤独', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='affect', description='感动', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='excitement', description='兴奋', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='happy', description='快乐', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='quiet', description='安静', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='miss', description='思念', category=curCategory, type=type_item_tag)

    '''
    以一种话题为依据的，这是主题
    '''
    curCategory = __getSpecCategroyItem(name='subject', description='主题', type=type_item_category)
    __getSpecTagItem(name='movie', description='影视', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='anime', description='动漫', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='show', description='演出、节目', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='schoolyard', description='校园', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='game', description='游戏', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='classical', description='经典', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='office', description='办公室', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='girl', description='美女', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='funny', description='搞笑', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='rank', description='榜单', category=curCategory, type=type_item_tag)
    __getSpecTagItem(name='hot', description='最受欢迎', category=curCategory, type=type_item_tag)


def init_all():
    '''
    初始化原始数据
    :return:
    '''
    print('call one ...')
    return

    type_data = __getSpecDataTypeItem(name='Data', description='基础的数据类型')
    type_item_category = __getSpecDataTypeItem(name='ItemCategory', description='Item分类的类型')
    type_set_category = __getSpecDataTypeItem(name='SetCategory', description='Set分类的类型')
    type_item_tag = __getSpecDataTypeItem(name='ItemTag', description='Item标签的类型')
    type_set_tag = __getSpecDataTypeItem(name='SetTag', description='Set标签的类型')
    type_user_analysis = __getSpecDataTypeItem(name='AnalysisType', description='分析数据类型')

    __initDataForItemAndSetCommon(type_item_category, type_item_tag)
    __initDataForItemAndSetCommon(type_set_category, type_set_tag)

    # 交叉使用import包，非全局引用，有效处理
    from api.gmagon.plugins.gif.test import init_test_data
    init_test_data()

    db.session.commit()


def api_session_commit():
    db.session.commit()


def api_checkSessionAdd(data_item):
    return __checkSessionAdd(data_item)


def api_getSpecDataTypeItem(name, description='', createNew=False):
    return __getSpecDataTypeItem(name, description, createNew=createNew)


def api_get_common_data_list(cls=None, filter=None, update_dict={}, createNew=True):
    return __get_data_with_filter_list(cls, filter, update_dict, createNew)

def api_get_data_with_filter_query(cls=None, filter=None):
    return __get_data_with_filter_query(cls, filter)


def api_getSpecDataTypeItemById(id):
    ele = DataTypes.query.filter_by(id=id).first()
    return ele


def api_getSpecCategroyItem(name, description='', type=None, parent=None, createNew=False):
    return __getSpecCategroyItem(name, description, type, parent, createNew=createNew)


def api_getSpecTagItem(name, description='', category=None, type=None, createNew=False):
    return __getSpecTagItem(name, description, category, type, createNew=createNew)
