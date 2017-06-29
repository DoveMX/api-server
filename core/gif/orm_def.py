#!/usr/bin/env python
# -*- coding: utf-8 -*-

# project
from ..database import db
from .common import constTablePrefix
from ..g_orm_def import GUserMachines

# self package
from datetime import datetime


class DataTypes(db.Model):
    '''
    资源基础数据罗类型 （全局类型）
    类似于C语言的枚举类型，每个值必须指定
    '''

    __tablename__ = constTablePrefix + 'types'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True, doc='唯一ID，ID需要自己来指定，不需要自动生成')
    name = db.Column(db.String(255), nullable=False, doc='数据类型的名称', unique=True)
    description = db.Column(db.String(400), nullable=False, doc='数据类型的描述')


class Categories(db.Model):
    '''
    资源基础数据分类类型（全局类型）
    支持子分类
    '''

    __tablename__ = constTablePrefix + 'categories'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(400), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'types.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'categories.id'), nullable=True)


class Tags(db.Model):
    '''
    资源基础数据标签（全局类型）
    '''

    __tablename__ = constTablePrefix + 'tags'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(400), nullable=False)
    category_id = db.Column(db.ForeignKey(constTablePrefix + 'categories.id'))
    type_id = db.Column(db.ForeignKey(constTablePrefix + 'types.id'), nullable=False)


class Item(db.Model):
    '''
    资源_$_item TABLE
    资源原始数据存储
    SEE ONLINE DOCUMENT: http://docs.sqlalchemy.org/en/latest/intro.html
    '''

    __tablename__ = constTablePrefix + 'item'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    thumb = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(400), nullable=False)
    tags = db.Column(db.String(255))
    categories = db.Column(db.String(255))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    active = db.Column(db.Boolean, nullable=False, default=True, doc='数据项是否处于激活状态，激活即为可用')
    copyright_protection = db.Column(db.Boolean, nullable=False, default=False, doc='数据项是否处于版权保护')
    is_shield = db.Column(db.Boolean, nullable=False, default=False, doc='是否被系统设置屏蔽')
    is_removed = db.Column(db.Boolean, nullable=False, default=False, doc='是否被标记移除')

    download_quantity = db.Column(db.Integer, default=0, nullable=False, doc='被下载的次数')
    preview_quantity = db.Column(db.Integer, default=0, nullable=False, doc='被浏览的次数')
    collection_quantity = db.Column(db.Integer, default=0, nullable=False, doc='被收藏的次数')
    share_quantity = db.Column(db.Integer, default=0, nullable=False, doc='被分享的次数')


class Set(db.Model):
    '''
    资源 素材包
    '''

    __tablename__ = constTablePrefix + 'set'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    thumb = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(400), nullable=False)
    tags = db.Column(db.String(255))
    categories = db.Column(db.String(255))
    create_time = db.Column(db.DateTime)

    active = db.Column(db.Boolean, nullable=False, default=True, doc='数据项是否处于激活状态，激活即为可用')
    copyright_protection = db.Column(db.Boolean, nullable=False, default=False, doc='数据项是否处于版权保护')
    is_shield = db.Column(db.Boolean, nullable=False, default=False, doc='是否被系统设置屏蔽')
    is_removed = db.Column(db.Boolean, nullable=False, default=False, doc='是否被标记移除')

    download_quantity = db.Column(db.Integer, default=0, nullable=False, doc='被下载的次数')
    preview_quantity = db.Column(db.Integer, default=0, nullable=False, doc='被浏览的次数')
    collection_quantity = db.Column(db.Integer, default=0, nullable=False, doc='被收藏的次数')
    share_quantity = db.Column(db.Integer, default=0, nullable=False, doc='被分享的次数')


class SetItems(db.Model):
    '''
    资源 素材包内容
    '''
    __tablename__ = constTablePrefix + 'set_items'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)

    set_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'set.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'item.id'), nullable=False)

    active = db.Column(db.Boolean, nullable=False, default=True, doc='数据项是否处于激活状态，激活即为可用')
    copyright_protection = db.Column(db.Boolean, nullable=False, default=False, doc='数据项是否处于版权保护')
    is_shield = db.Column(db.Boolean, nullable=False, default=False, doc='是否被系统设置屏蔽')
    is_removed = db.Column(db.Boolean, nullable=False, default=False, doc='是否被标记移除')

    set = db.relationship("Set", backref=db.backref(__tablename__, order_by=id))
    item = db.relationship("Item", backref=db.backref(__tablename__, order_by=id))


### 评论部分
class CommentsForItem(db.Model):
    '''
    评论针对单个资源文件的
    '''
    __tablename__ = constTablePrefix + 'comments_for_item'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'item.id'), nullable=False)

    user_id = db.Column(db.String(255), db.ForeignKey(constTablePrefix + 'user.id'), nullable=False)
    comment = db.Column(db.Text(2000), nullable=False)
    tags = db.Column(db.String(255))
    categories = db.Column(db.String(255))

    parent_id = db.Column(db.Integer, db.ForeignKey(__tablename__ + '.id'))  ## 针对的上一级评论

    is_shield = db.Column(db.Boolean, nullable=False, default=False, doc='是否被系统设置屏蔽')
    is_removed = db.Column(db.Boolean, nullable=False, default=False, doc='是否被标记移除')

    history = db.Column(db.Text(10000), nullable=False, default='', doc='历史记录，json数据类型')

    modify_time = db.Column(db.DateTime)
    create_time = db.Column(db.DateTime)


class CommentsForSet(db.Model):
    '''
    评论针对资源素材包
    '''

    __tablename__ = constTablePrefix + 'comments_for_set'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    set_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'set.id'), nullable=False)

    user_id = db.Column(db.String(255), db.ForeignKey(constTablePrefix + 'user.id'), nullable=False)
    comment = db.Column(db.Text(2000), nullable=False)
    tags = db.Column(db.String(255))
    categories = db.Column(db.String(255))

    parent_id = db.Column(db.Integer, db.ForeignKey(__tablename__ + '.id'))  ## 针对的上一级评论

    is_shield = db.Column(db.Boolean, nullable=False, default=False, doc='是否被系统设置屏蔽')
    is_removed = db.Column(db.Boolean, nullable=False, default=False, doc='是否被标记移除')

    history = db.Column(db.Text(10000), nullable=False, default='', doc='历史记录，json数据类型')

    modify_time = db.Column(db.DateTime)
    create_time = db.Column(db.DateTime)


### 用户部分
class User(db.Model):
    '''
    资源专区的用户
    '''
    __tablename__ = constTablePrefix + 'user'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)

    machine_id = db.Column(db.String(255), db.ForeignKey('machines.id'), doc='唯一ID')  # 存储真实的机器码
    machine = db.relationship('GUserMachines', backref='gif_user')
    create_time = db.Column(db.DateTime)


class UserTrace(db.Model):
    '''
    针对用户的操作跟踪，为后面分析用户行为及数据做准备
    '''

    __tablename__ = constTablePrefix + 'user_trace'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey(constTablePrefix + 'user.id'), nullable=False)
    type = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'types.id'), nullable=False)
    content = db.Column(db.Text, nullable=False, default='')
    create_time = db.Column(db.DateTime)


class UserPush(db.Model):
    '''
    根据用户的习惯（从用户的行为中分析得来），推荐给用户一些自动化的信息
    '''
    __tablename__ = constTablePrefix + 'user_push'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='向谁推送')
    type = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'types.id'), nullable=False, doc='推送的类型')

    title = db.Column(db.String(255), doc='推送内容的标题')
    subtitle = db.Column(db.String(512), doc='推送内容的子标题')

    content = db.Column(db.Text, nullable=False, default='', doc='推送的内容的JSON字符串')

    download_quantity = db.Column(db.Integer, default=0, nullable=False, doc='被下载的次数')
    preview_quantity = db.Column(db.Integer, default=0, nullable=False, doc='被浏览的次数')
    collection_quantity = db.Column(db.Integer, default=0, nullable=False, doc='被收藏的次数')
    share_quantity = db.Column(db.Integer, default=0, nullable=False, doc='被分享的次数')

    create_time = db.Column(db.DateTime)


class UserAnalysisAUTO(db.Model):
    '''
    根据用户的习惯（从用户的行为中分析得来），推荐给用户一些自动化的信息
    '''
    __tablename__ = constTablePrefix + 'user_analysis_auto'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='分析谁')
    type = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'types.id'), nullable=False, doc='分析的数据类型')
    content = db.Column(db.Text, nullable=False, default='', doc='分析的结果')

    create_time = db.Column(db.DateTime)


class TraceItemDownload(db.Model):
    '''
    跟踪资源图片的下载情况
    '''
    __tablename__ = constTablePrefix + 'trace_item_download'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)

    item_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'item.id'), nullable=False)
    user_id = db.Column(db.String(255), db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='谁')
    create_time = db.Column(db.DateTime)


class TraceItemPreview(db.Model):
    '''
    跟踪资源图片的浏览情况
    '''
    __tablename__ = constTablePrefix + 'trace_item_preview'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)

    item_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'item.id'), nullable=False)
    user_id = db.Column(db.String(255), db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='谁')
    create_time = db.Column(db.DateTime)


class TraceItemCollection(db.Model):
    '''
    跟踪资源图片的收藏情况
    '''
    __tablename__ = constTablePrefix + 'trace_item_collection'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)

    item_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'item.id'), nullable=False)
    user_id = db.Column(db.String(255), db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='谁')
    create_time = db.Column(db.DateTime)


class TraceItemShare(db.Model):
    '''
    跟踪资源图片的收藏情况
    '''
    __tablename__ = constTablePrefix + 'trace_item_share'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)

    item_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'item.id'), nullable=False)
    user_id = db.Column(db.String(255), db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='谁')
    create_time = db.Column(db.DateTime)


class TraceSetDownload(db.Model):
    '''
    跟踪资源素材包的下载情况
    '''
    __tablename__ = constTablePrefix + 'trace_set_download'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)

    item_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'item.id'), nullable=False)
    user_id = db.Column(db.String(255), db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='谁')
    create_time = db.Column(db.DateTime)


class TraceSetPreview(db.Model):
    '''
    跟踪资源素材包的浏览情况
    '''
    __tablename__ = constTablePrefix + 'trace_set_preview'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)

    item_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'item.id'), nullable=False)
    user_id = db.Column(db.String(255), db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='谁')
    create_time = db.Column(db.DateTime)


class TraceSetCollection(db.Model):
    '''
    跟踪资源素材包的收藏情况
    '''
    __tablename__ = constTablePrefix + 'trace_set_collection'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)

    item_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'item.id'), nullable=False)
    user_id = db.Column(db.String(255), db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='谁')
    create_time = db.Column(db.DateTime)


class TraceSetShare(db.Model):
    '''
    跟踪资源素材包的收藏情况
    '''
    __tablename__ = constTablePrefix + 'trace_set_share'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)

    item_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'item.id'), nullable=False)
    user_id = db.Column(db.String(255), db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='谁')
    create_time = db.Column(db.DateTime)


'''
RelationShip
'''

## DataTypes
DataTypes.categories = db.relationship('Categories', backref='type', order_by=Categories.id)
DataTypes.tags = db.relationship('Tags', backref='type', order_by=Tags.id)

##See: https://stackoverflow.com/questions/6782133/sqlalchemy-one-to-many-relationship-on-single-table-inheritance-declarative
Categories.children = db.relationship('Categories', backref='parent', remote_side=Categories.id)
Categories.tags = db.relationship('Tags', backref='category', order_by=Tags.id)

