#!/usr/bin/env python
# -*- coding: utf-8 -*-

# self package
from datetime import datetime

# project
from api.gmagon.database import db
from api.gmagon.plugins.gif.constant import constTablePrefix


class DataTypes(db.Model):
    '''
    资源基础数据罗类型 （全局类型）
    类似于C语言的枚举类型，每个值必须指定
    '''

    __tablename__ = constTablePrefix + 'types'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True,
                   doc='唯一ID，ID需要自己来指定，不需要自动生成')
    name = db.Column(db.String(255), nullable=False, doc='数据类型的名称', unique=True)
    description = db.Column(db.String(400), nullable=False, doc='数据类型的描述')

    def getJSON(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


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

    def getJSON(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type_id': self.type_id,
            'type_name': self.type.name,
            'parent_id': self.parent_id if self.parent_id else '',
            'parent_name': self.parent.name if self.parent else ''
        }


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

    def getJSON(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category_id': self.category_id,
            'category_name': self.category.name,
            'type_id': self.type_id,
            'type_name': self.type.name
        }


'''
Many-to-Many Relationships
'''
tbl_item_tags = db.Table(constTablePrefix + 'item_tags',
                         db.Column('item_id', db.ForeignKey(constTablePrefix + 'item.id'), nullable=False,
                                   primary_key=True),
                         db.Column('tag_id', db.ForeignKey(constTablePrefix + 'tags.id'), nullable=False,
                                   primary_key=True)
                         )
tbl_item_categories = db.Table(constTablePrefix + 'item_categories',
                         db.Column('item_id', db.ForeignKey(constTablePrefix + 'item.id'), nullable=False,
                                   primary_key=True),
                         db.Column('category_id', db.ForeignKey(constTablePrefix + 'categories.id'), nullable=False,
                                   primary_key=True)
                         )

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
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    active = db.Column(db.Boolean, nullable=False, default=True, doc='数据项是否处于激活状态，激活即为可用')
    copyright_protection = db.Column(db.Boolean, nullable=False, default=False, doc='数据项是否处于版权保护')
    is_shield = db.Column(db.Boolean, nullable=False, default=False, doc='是否被系统设置屏蔽')
    is_removed = db.Column(db.Boolean, nullable=False, default=False, doc='是否被标记移除')

    download_quantity = db.Column(db.Integer, default=0, nullable=False, doc='被下载的次数')
    preview_quantity = db.Column(db.Integer, default=0, nullable=False, doc='被浏览的次数')
    collection_quantity = db.Column(db.Integer, default=0, nullable=False, doc='被收藏的次数')
    share_quantity = db.Column(db.Integer, default=0, nullable=False, doc='被分享的次数')

    tags = db.relationship('Tags', secondary=tbl_item_tags, backref=db.backref('items', lazy='dynamic'))
    categories = db.relationship('Categories', secondary=tbl_item_categories, backref=db.backref('items', lazy='dynamic'))

    def getJSON(self):
        """
        获取可JSON化的数据
        :return:
        """
        tagsDataList = []
        for tagObj in self.tags:
            ele_tag = tagObj.getJSON()
            tagsDataList.append(ele_tag)

        categoriesDataList = []
        for categoryObj in self.categories:
            ele_category = categoryObj.getJSON()
            categoriesDataList.append(ele_category)

        return {
            'id': self.id,
            'name': self.name,
            'thumb': self.thumb,
            'url': self.url,
            'description': self.description,
            'create_time': self.create_time,

            'active': self.active,
            'copyright_protection': self.copyright_protection,
            'is_shield': self.is_shield,
            'is_removed': self.is_removed,

            'download_quantity': self.download_quantity,
            'preview_quantity': self.preview_quantity,
            'collection_quantity': self.collection_quantity,
            'share_quantity': self.share_quantity,

            'tags': tagsDataList,
            'categories': categoriesDataList
        }

'''
Many-to-Many Relationships
'''
#Note 素材包标签表
tbl_set_tags = db.Table(constTablePrefix + 'set_tags',
                         db.Column('set_id', db.ForeignKey(constTablePrefix + 'set.id'), nullable=False,
                                   primary_key=True),
                         db.Column('tag_id', db.ForeignKey(constTablePrefix + 'tags.id'), nullable=False,
                                   primary_key=True)
                         )

#Note 素材包分类表
tbl_set_categories = db.Table(constTablePrefix + 'set_categories',
                         db.Column('set_id', db.ForeignKey(constTablePrefix + 'set.id'), nullable=False,
                                   primary_key=True),
                         db.Column('category_id', db.ForeignKey(constTablePrefix + 'categories.id'), nullable=False,
                                   primary_key=True)
                         )

#Note 资源&素材包表
tbl_set_items = db.Table(constTablePrefix + 'set_items',
                         db.Column('set_id', db.ForeignKey(constTablePrefix + 'set.id'), nullable=False,
                                   primary_key=True),
                         db.Column('item_id', db.ForeignKey(constTablePrefix + 'item.id'), nullable=False,
                                   primary_key=True),
                         db.Column('active', db.Boolean, nullable=False, default=True, doc='数据项是否处于激活状态，激活即为可用'),
                         db.Column('copyright_protection', db.Boolean, nullable=False, default=False, doc='数据项是否处于版权保护'),
                         db.Column('is_shield', db.Boolean, nullable=False, default=False, doc='是否被系统设置屏蔽'),
                         db.Column('is_removed', db.Boolean, nullable=False, default=False, doc='是否被标记移除')
                         )

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
    create_time = db.Column(db.DateTime)

    active = db.Column(db.Boolean, nullable=False, default=True, doc='数据项是否处于激活状态，激活即为可用')
    copyright_protection = db.Column(db.Boolean, nullable=False, default=False, doc='数据项是否处于版权保护')
    is_shield = db.Column(db.Boolean, nullable=False, default=False, doc='是否被系统设置屏蔽')
    is_removed = db.Column(db.Boolean, nullable=False, default=False, doc='是否被标记移除')

    download_quantity = db.Column(db.Integer, default=0, nullable=False, doc='被下载的次数')
    preview_quantity = db.Column(db.Integer, default=0, nullable=False, doc='被浏览的次数')
    collection_quantity = db.Column(db.Integer, default=0, nullable=False, doc='被收藏的次数')
    share_quantity = db.Column(db.Integer, default=0, nullable=False, doc='被分享的次数')

    tags = db.relationship('Tags', secondary=tbl_set_tags, backref=db.backref('sets', lazy='dynamic'))
    categories = db.relationship('Categories', secondary=tbl_set_categories, backref=db.backref('sets', lazy='dynamic'))
    items = db.relationship('Item', secondary=tbl_set_items, backref=db.backref('sets', lazy='dynamic'))



### 评论部分
class CommentsForItem(db.Model):
    '''
    评论针对单个资源文件的
    '''
    __tablename__ = constTablePrefix + 'comments_for_item'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'item.id'), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'user.id'), nullable=False)
    comment = db.Column(db.Text(2000), nullable=False)

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

    user_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'user.id'), nullable=False)
    comment = db.Column(db.Text(2000), nullable=False)

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

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)

    machine_id = db.Column(db.String(255), db.ForeignKey('machines.id'), doc='唯一ID')  # 存储真实的机器码
    create_time = db.Column(db.DateTime)

    machine = db.relationship('GUserMachines', backref='gif_user')


class UserTrace(db.Model):
    '''
    针对用户的操作跟踪，为后面分析用户行为及数据做准备
    '''

    __tablename__ = constTablePrefix + 'user_trace'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'user.id'), nullable=False)
    type = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'types.id'), nullable=False)
    content = db.Column(db.Text, nullable=False, default='')
    create_time = db.Column(db.DateTime)


class UserPush(db.Model):
    '''
    根据用户的习惯（从用户的行为中分析得来），推荐给用户一些自动化的信息
    '''
    __tablename__ = constTablePrefix + 'user_push'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='向谁推送')
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
    user_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='分析谁')
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
    user_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='谁')
    create_time = db.Column(db.DateTime)


class TraceItemPreview(db.Model):
    '''
    跟踪资源图片的浏览情况
    '''
    __tablename__ = constTablePrefix + 'trace_item_preview'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)

    item_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'item.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='谁')
    create_time = db.Column(db.DateTime)


class TraceItemCollection(db.Model):
    '''
    跟踪资源图片的收藏情况
    '''
    __tablename__ = constTablePrefix + 'trace_item_collection'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)

    item_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'item.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='谁')
    create_time = db.Column(db.DateTime)


class TraceItemShare(db.Model):
    '''
    跟踪资源图片的收藏情况
    '''
    __tablename__ = constTablePrefix + 'trace_item_share'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)

    item_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'item.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='谁')
    create_time = db.Column(db.DateTime)


class TraceSetDownload(db.Model):
    '''
    跟踪资源素材包的下载情况
    '''
    __tablename__ = constTablePrefix + 'trace_set_download'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)

    item_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'item.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='谁')
    create_time = db.Column(db.DateTime)


class TraceSetPreview(db.Model):
    '''
    跟踪资源素材包的浏览情况
    '''
    __tablename__ = constTablePrefix + 'trace_set_preview'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)

    item_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'item.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='谁')
    create_time = db.Column(db.DateTime)


class TraceSetCollection(db.Model):
    '''
    跟踪资源素材包的收藏情况
    '''
    __tablename__ = constTablePrefix + 'trace_set_collection'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)

    item_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'item.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='谁')
    create_time = db.Column(db.DateTime)


class TraceSetShare(db.Model):
    '''
    跟踪资源素材包的收藏情况
    '''
    __tablename__ = constTablePrefix + 'trace_set_share'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)

    item_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'item.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='谁')
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
