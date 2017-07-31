#!/usr/bin/env python
# -*- coding: utf-8 -*-

# system package
from datetime import datetime

import types
# libs
from sqlalchemy.ext.orderinglist import ordering_list

from gmagon.common.util import format_datetime
# project
from gmagon.database import db
from gmagon.plugins.gif.util import constTablePrefix


class _Utils:
    @staticmethod
    def calc_user_op_statistics_count(query):
        """统计与用户相关的常用操作数量"""
        info = {
            'count': 0,
            'download': 0,
            'preview': 0,
            'collection': 0,
            'share': 0
        }

        if query is None:
            return info

        info['count'] = query.count()
        for item in query:
            info['download'] += item.download_users.count()
            info['preview'] += item.preview_users.count()
            info['collection'] += item.collection_users.count()
            info['share'] += item.share_users.count()

        return info

    @staticmethod
    def calc_list(query):
        data_list = []
        if query is None:
            return data_list

        for ele in query:
            if hasattr(ele, 'getBaseJSON'):
                data_list.append(ele.getBaseJSON())
        return data_list

    @staticmethod
    def auto_calc_count(obj):
        if isinstance(obj, db.Query):
            return obj.count()
        elif isinstance(obj, types.ListType):
            return len(obj)
        elif obj is None:
            return 0
        else:
            print('no match the obj type = %s' % type(obj))


class DataTypes(db.Model):
    """
    资源基础数据罗类型 （全局类型）
    类似于C语言的枚举类型，每个值必须指定
    """

    __tablename__ = constTablePrefix + 'types'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True,
                   doc='唯一ID，ID需要自己来指定，不需要自动生成')
    name = db.Column(db.String(255), nullable=False, doc='数据类型的名称', unique=True)
    description = db.Column(db.String(400), nullable=False, default='', doc='数据类型的描述')

    def getBaseJSON(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

    def getJSON(self):
        info = self.getBaseJSON()
        return info

    def getJSONEx(self):
        info = self.getBaseJSON()
        return info

    def __repr__(self):
        return "DataTypes(%d, %s, %s)" % (self.id, self.name, self.description)


class Categories(db.Model):
    """
    资源基础数据分类类型（全局类型）
    支持子分类
    """

    __tablename__ = constTablePrefix + 'categories'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    thumb = db.Column(db.String(255), default='')
    description = db.Column(db.String(4000), nullable=False, doc='简介')
    type_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'types.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'categories.id'), nullable=True)

    def getBaseJSON(self):
        return {
            'id': self.id,
            'name': self.name,
            'thumb': self.thumb,
            'description': self.description,
            'type_id': self.type_id,
            'type_name': self.type.name,
            'parent_id': self.parent_id if self.parent_id else '',
            'parent_name': self.parent.name if self.parent else ''
        }

    def getJSON(self):
        info = self.getBaseJSON()
        info.update({
            'items_count': _Utils.auto_calc_count(self.items),
            'sets_count': _Utils.auto_calc_count(self.sets),
            'tags_count': _Utils.auto_calc_count(self.tags),
            'children_count': _Utils.auto_calc_count(self.children)
        })
        return info

    def getJSONEx(self, more=True):
        info = self.getJSON()
        info.update({
            'items_statistics': _Utils.calc_user_op_statistics_count(self.items),
            'sets_statistics': _Utils.calc_user_op_statistics_count(self.sets),
        })

        if more:
            info.update({
                'children': _Utils.calc_list(self.children),
                'tags': _Utils.calc_list(self.tags),
                'items': _Utils.calc_list(self.items),
                'sets': _Utils.calc_list(self.sets)
            })
        return info


class Tags(db.Model):
    """
    资源基础数据标签（全局类型）
    """

    __tablename__ = constTablePrefix + 'tags'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    thumb = db.Column(db.String(255), default='')
    description = db.Column(db.String(4000), nullable=False, doc='简介')
    category_id = db.Column(db.ForeignKey(constTablePrefix + 'categories.id'))
    type_id = db.Column(db.ForeignKey(constTablePrefix + 'types.id'), nullable=False)
    category = db.relationship('Categories', backref='tags')

    def getBaseJSON(self):
        return {
            'id': self.id,
            'name': self.name,
            'thumb': self.thumb,
            'description': self.description,
            'category_id': self.category_id,
            'category_name': self.category.name,
            'type_id': self.type_id,
            'type_name': self.type.name,
        }

    def getJSON(self):
        info = self.getBaseJSON()
        info.update({
            'items_count': _Utils.auto_calc_count(self.items),
            'sets_count': _Utils.auto_calc_count(self.sets),
        })
        return info

    def getJSONEx(self, more=True):
        info = self.getJSON()
        info.update({
            'items_statistics': _Utils.calc_user_op_statistics_count(self.items),
            'sets_statistics': _Utils.calc_user_op_statistics_count(self.sets),
        })

        if more:
            info.update({
                'items': _Utils.calc_list(self.items),
                'sets': _Utils.calc_list(self.sets)
            })

        return info


# 用户部分
tbl_followers = db.Table(constTablePrefix + 'followers',
                         db.Column('follower_id', db.Integer, db.ForeignKey(constTablePrefix + 'user.id')),
                         db.Column('followed_id', db.Integer, db.ForeignKey(constTablePrefix + 'user.id'))
                         )


class User(db.Model):
    """
    资源专区的用户
    """
    __tablename__ = constTablePrefix + 'user'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联的机器码
    machine_id = db.Column(db.String(255), db.ForeignKey('machines.id'), nullable=False, unique=True,
                           doc='唯一ID')  # 存储真实的机器码
    machine = db.relationship('GUserMachines', backref='gif_user')

    # 关注与被关注
    followed = db.relationship('User',
                               secondary=tbl_followers,
                               primaryjoin=(tbl_followers.c.follower_id == id),
                               secondaryjoin=(tbl_followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(tbl_followers.c.followed_id == user.id).count() > 0

    def getJSON(self):
        return {
            'id': self.id,
            'machine_id': self.machine_id,
        }


class UserTrace(db.Model):
    """
    针对用户的操作跟踪，为后面分析用户行为及数据做准备
    """

    __tablename__ = constTablePrefix + 'user_trace'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'user.id'), nullable=False)
    type = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'types.id'), nullable=False)
    content = db.Column(db.Text, nullable=False, default='')
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


class UserPush(db.Model):
    """
    根据用户的习惯（从用户的行为中分析得来），推荐给用户一些自动化的信息
    """
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

    create_time = db.Column(db.DateTime, default=datetime.utcnow)


class UserAnalysisAUTO(db.Model):
    """
    根据用户的习惯（从用户的行为中分析得来），推荐给用户一些自动化的信息
    """
    __tablename__ = constTablePrefix + 'user_analysis_auto'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='分析谁')
    type = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'types.id'), nullable=False, doc='分析的数据类型')
    content = db.Column(db.Text, nullable=False, default='', doc='分析的结果')

    create_time = db.Column(db.DateTime, default=datetime.utcnow)


##############
class SetToItems(db.Model):
    __tablename__ = constTablePrefix + 'set_items'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    set_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'set.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'item.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0, doc='排序')
    bewrite = db.Column(db.String(4000), nullable=True, default='', doc='针对该Item在Set中的介绍，有别于Item自己的描述')

    active = db.Column(db.Boolean, nullable=False, default=True, doc='数据项是否处于激活状态，激活即为可用')
    copyright_protection = db.Column(db.Boolean, nullable=False, default=False, doc='数据项是否处于版权保护')
    is_shield = db.Column(db.Boolean, nullable=False, default=False, doc='是否被系统设置屏蔽')
    is_removed = db.Column(db.Boolean, nullable=False, default=False, doc='是否被标记移除')

    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    def getBaseJSON(self):
        return {
            'id': self.id,
            'set_id': self.set_id,
            'item_id': self.item_id,

            'order': self.order,
            'bewrite': self.bewrite,

            'active': self.active,
            'copyright_protection': self.copyright_protection,
            'is_shield': self.is_shield,
            'is_removed': self.is_removed,

            'create_time': format_datetime(self.create_time)
        }


    def getJSON(self):
        info = self.getBaseJSON()
        return info


    def getJSONEx(self, more=True):
        info = self.getJSON()
        return info

##############
"""
Many-to-Many Relationships
"""
tbl_item_tags = db.Table(constTablePrefix + 'item_tags',
                         db.Column('item_id', db.ForeignKey(constTablePrefix + 'item.id'), nullable=False,
                                   primary_key=True),
                         db.Column('tag_id', db.ForeignKey(constTablePrefix + 'tags.id'), nullable=False,
                                   primary_key=True),
                         db.Column('create_time', db.DateTime, default=datetime.utcnow)
                         )
tbl_item_categories = db.Table(constTablePrefix + 'item_categories',
                               db.Column('item_id', db.ForeignKey(constTablePrefix + 'item.id'), nullable=False,
                                         primary_key=True),
                               db.Column('category_id', db.ForeignKey(constTablePrefix + 'categories.id'),
                                         nullable=False,
                                         primary_key=True),
                               db.Column('create_time', db.DateTime, default=datetime.utcnow)
                               )

"""下载
"""
tbl_item_trace_downloads = db.Table(constTablePrefix + 'trace_item_downloads',
                                    db.Column('id', db.Integer,
                                              db.Sequence(constTablePrefix + 'trace_item_downloads' + '_id_seq'),
                                              autoincrement=True, primary_key=True),
                                    db.Column('item_id', db.ForeignKey(constTablePrefix + 'item.id'), nullable=False),
                                    db.Column('user_id', db.ForeignKey(constTablePrefix + 'user.id'), nullable=False),
                                    db.Column('create_time', db.DateTime, default=datetime.utcnow)
                                    )
"""浏览，类似于试听
"""
tbl_item_trace_previews = db.Table(constTablePrefix + 'trace_item_previews',
                                   db.Column('id', db.Integer,
                                             db.Sequence(constTablePrefix + 'trace_item_previews' + '_id_seq'),
                                             autoincrement=True, primary_key=True),
                                   db.Column('item_id', db.ForeignKey(constTablePrefix + 'item.id'), nullable=False),
                                   db.Column('user_id', db.ForeignKey(constTablePrefix + 'user.id'), nullable=False),
                                   db.Column('create_time', db.DateTime, default=datetime.utcnow)
                                   )

"""收藏
"""
tbl_item_trace_collections = db.Table(constTablePrefix + 'trace_item_collections',
                                      db.Column('id', db.Integer,
                                                db.Sequence(constTablePrefix + 'trace_item_collections' + '_id_seq'),
                                                autoincrement=True, primary_key=True),
                                      db.Column('item_id', db.ForeignKey(constTablePrefix + 'item.id'), nullable=False),
                                      db.Column('user_id', db.ForeignKey(constTablePrefix + 'user.id'), nullable=False),
                                      db.Column('create_time', db.DateTime, default=datetime.utcnow)
                                      )
"""分享
"""
tbl_item_trace_shares = db.Table(constTablePrefix + 'trace_item_shares',
                                 db.Column('id', db.Integer,
                                           db.Sequence(constTablePrefix + 'trace_item_shares' + '_id_seq'),
                                           autoincrement=True, primary_key=True),
                                 db.Column('item_id', db.ForeignKey(constTablePrefix + 'item.id'), nullable=False),
                                 db.Column('user_id', db.ForeignKey(constTablePrefix + 'user.id'), nullable=False),
                                 db.Column('create_time', db.DateTime, default=datetime.utcnow)
                                 )


class Item(db.Model):
    """
    资源_$_item TABLE
    资源原始数据存储
    SEE ONLINE DOCUMENT: http://docs.sqlalchemy.org/en/latest/intro.html
    """

    __tablename__ = constTablePrefix + 'item'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    thumb = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    size = db.Column(db.Integer, nullable=True, doc='文件大小')
    dimensions = db.Column(db.String(32), default='0x0', nullable=True, doc='图片尺寸规格')
    ext = db.Column(db.String(12), nullable=True, default='gif', doc='文件扩展名')
    md5 = db.Column(db.String(512), nullable=True, doc='文件的md5值')
    description = db.Column(db.String(4000), nullable=False, doc='简介')
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    active = db.Column(db.Boolean, nullable=False, default=True, doc='数据项是否处于激活状态，激活即为可用')
    copyright_protection = db.Column(db.Boolean, nullable=False, default=False, doc='数据项是否处于版权保护')
    is_shield = db.Column(db.Boolean, nullable=False, default=False, doc='是否被系统设置屏蔽')
    is_removed = db.Column(db.Boolean, nullable=False, default=False, doc='是否被标记移除')

    """Relations
    """
    tags = db.relationship('Tags', secondary=tbl_item_tags,
                           backref=db.backref('items', lazy='dynamic'), lazy='dynamic')
    categories = db.relationship('Categories', secondary=tbl_item_categories,
                                 backref=db.backref('items', lazy='dynamic'), lazy='dynamic')

    # 跟踪信息
    download_users = db.relationship('User', secondary=tbl_item_trace_downloads,
                                     backref=db.backref('download_items', lazy='dynamic'), lazy='dynamic')
    preview_users = db.relationship('User', secondary=tbl_item_trace_previews,
                                    backref=db.backref('preview_items', lazy='dynamic'), lazy='dynamic')
    collection_users = db.relationship('User', secondary=tbl_item_trace_collections,
                                       backref=db.backref('collection_items', lazy='dynamic'), lazy='dynamic')
    share_users = db.relationship('User', secondary=tbl_item_trace_shares,
                                  backref=db.backref('share_items', lazy='dynamic'), lazy='dynamic')

    def getBaseJSON(self):
        return {
            'id': self.id,
            'name': self.name,
            'thumb': self.thumb,
            'url': self.url,
            'description': self.description,
            'create_time': format_datetime(self.create_time),

            'active': self.active,
            'copyright_protection': self.copyright_protection,
            'is_shield': self.is_shield,
            'is_removed': self.is_removed,

            'download_quantity': self.download_users.count(),
            'preview_quantity': self.preview_users.count(),
            'collection_quantity': self.collection_users.count(),
            'share_quantity': self.share_users.count()
        }

    def getJSON(self):
        info = self.getBaseJSON()
        info.update({
            'tags_count': _Utils.auto_calc_count(self.tags),
            'categories_count': _Utils.auto_calc_count(self.categories),
            'sets_count': _Utils.auto_calc_count(self.sets),
        })
        return info

    def getJSONEx(self):
        """
        获取可JSON化的数据
        :return:
        """

        info = self.getJSON()
        info.update({
            'tags': _Utils.calc_list(self.tags),
            'categories': _Utils.calc_list(self.categories),
            'sets': _Utils.calc_list(self.sets),
        })
        return info

    @staticmethod
    def sort_items_by_tag_id(tag_id):
        return Item.query.join(tbl_item_tags,
                               (tbl_item_tags.c.tag_id == tag_id)).filter(tbl_item_tags.c.item_id == Item.id) \
            .order_by(Item.id.desc()).filter()

    @staticmethod
    def sort_items_by_category_id(category_id):
        return Item.query.join(tbl_item_categories,
                               (tbl_item_categories.c.category_id == category_id)).filter(
            tbl_item_categories.c.item_id == Item.id) \
            .order_by(Item.id.desc()).filter()

    @staticmethod
    def common_sort_users_by_item_id(item_id, props='download_users'):
        cur_item = Item.query.filter_by(id=item_id).first()
        query = None
        if cur_item:
            query = cur_item.__getattribute__(props)
        return query


"""
Many-to-Many Relationships
"""
# Note 素材包标签表
tbl_set_tags = db.Table(constTablePrefix + 'set_tags',
                        db.Column('set_id', db.ForeignKey(constTablePrefix + 'set.id'), nullable=False,
                                  primary_key=True),
                        db.Column('tag_id', db.ForeignKey(constTablePrefix + 'tags.id'), nullable=False,
                                  primary_key=True)
                        )

# Note 素材包分类表
tbl_set_categories = db.Table(constTablePrefix + 'set_categories',
                              db.Column('set_id', db.ForeignKey(constTablePrefix + 'set.id'), nullable=False,
                                        primary_key=True),
                              db.Column('category_id', db.ForeignKey(constTablePrefix + 'categories.id'),
                                        nullable=False,
                                        primary_key=True)
                              )

# Note 资源&素材包表
# SetToItems.__table__ = db.Table(constTablePrefix + 'set_items',
#                          db.Column('set_id', db.ForeignKey(constTablePrefix + 'set.id'), nullable=False,
#                                    primary_key=True),
#                          db.Column('item_id', db.ForeignKey(constTablePrefix + 'item.id'), nullable=False,
#                                    primary_key=True),
#                          db.Column('order', db.Integer, nullable=False, default=0, doc='排序'),
#                          db.Column('bewrite', db.String(4000), nullable=True, default='',
#                                    doc='针对该Item在Set中的介绍，有别于Item自己的描述'),
#
#                          db.Column('active', db.Boolean, nullable=False, default=True, doc='数据项是否处于激活状态，激活即为可用'),
#                          db.Column('copyright_protection', db.Boolean, nullable=False, default=False,
#                                    doc='数据项是否处于版权保护'),
#                          db.Column('is_shield', db.Boolean, nullable=False, default=False, doc='是否被系统设置屏蔽'),
#                          db.Column('is_removed', db.Boolean, nullable=False, default=False, doc='是否被标记移除')
#                          )

"""下载
"""
tbl_set_trace_downloads = db.Table(constTablePrefix + 'trace_set_downloads',
                                   db.Column('id', db.Integer,
                                             db.Sequence(constTablePrefix + 'trace_set_downloads' + '_id_seq'),
                                             autoincrement=True, primary_key=True),
                                   db.Column('set_id', db.ForeignKey(constTablePrefix + 'set.id'), nullable=False),
                                   db.Column('user_id', db.ForeignKey(constTablePrefix + 'user.id'), nullable=False),
                                   db.Column('create_time', db.DateTime, default=datetime.utcnow)
                                   )
"""
浏览，类似于试听
"""
tbl_set_trace_previews = db.Table(constTablePrefix + 'trace_set_previews',
                                  db.Column('id', db.Integer,
                                            db.Sequence(constTablePrefix + 'trace_set_previews' + '_id_seq'),
                                            autoincrement=True, primary_key=True),
                                  db.Column('set_id', db.ForeignKey(constTablePrefix + 'set.id'), nullable=False),
                                  db.Column('user_id', db.ForeignKey(constTablePrefix + 'user.id'), nullable=False),
                                  db.Column('create_time', db.DateTime, default=datetime.utcnow)
                                  )

"""收藏
"""
tbl_set_trace_collections = db.Table(constTablePrefix + 'trace_set_collections',
                                     db.Column('id', db.Integer,
                                               db.Sequence(constTablePrefix + 'trace_set_collections' + '_id_seq'),
                                               autoincrement=True, primary_key=True),
                                     db.Column('set_id', db.ForeignKey(constTablePrefix + 'set.id'), nullable=False),
                                     db.Column('user_id', db.ForeignKey(constTablePrefix + 'user.id'), nullable=False),
                                     db.Column('create_time', db.DateTime, default=datetime.utcnow)
                                     )
"""分享
"""
tbl_set_trace_shares = db.Table(constTablePrefix + 'trace_set_shares',
                                db.Column('id', db.Integer,
                                          db.Sequence(constTablePrefix + 'trace_set_shares' + '_id_seq'),
                                          autoincrement=True, primary_key=True),
                                db.Column('set_id', db.ForeignKey(constTablePrefix + 'set.id'), nullable=False),
                                db.Column('user_id', db.ForeignKey(constTablePrefix + 'user.id'), nullable=False),
                                db.Column('create_time', db.DateTime, default=datetime.utcnow)
                                )


class Set(db.Model):
    """
    资源 素材包, 可以以专辑，歌单，资源库等分类方式出现
    """

    __tablename__ = constTablePrefix + 'set'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    thumb = db.Column(db.String(255), nullable=False, doc='封面')
    url = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(4000), nullable=False, doc='简介')
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    active = db.Column(db.Boolean, nullable=False, default=True, doc='数据项是否处于激活状态，激活即为可用')
    copyright_protection = db.Column(db.Boolean, nullable=False, default=False, doc='数据项是否处于版权保护')
    is_shield = db.Column(db.Boolean, nullable=False, default=False, doc='是否被系统设置屏蔽')
    is_removed = db.Column(db.Boolean, nullable=False, default=False, doc='是否被标记移除')

    tags = db.relationship('Tags', secondary=tbl_set_tags,
                           primaryjoin=id == tbl_set_tags.c.set_id,
                           backref=db.backref('sets', lazy='dynamic'), lazy='dynamic')
    categories = db.relationship('Categories', secondary=tbl_set_categories,
                                 primaryjoin=id == tbl_set_categories.c.set_id,
                                 backref=db.backref('sets', lazy='dynamic'), lazy='dynamic')

    items = db.relationship('Item', secondary=SetToItems.__table__,
                            primaryjoin=(id == SetToItems.__table__.c.set_id),
                            order_by=SetToItems.__table__.c.order.asc(),
                            collection_class=ordering_list(SetToItems.__table__.c.order),
                            backref=db.backref('sets', lazy='dynamic'), lazy='dynamic')

    # 跟踪信息
    download_users = db.relationship('User', secondary=tbl_set_trace_downloads,
                                     backref=db.backref('download_sets', lazy='dynamic'), lazy='dynamic')
    preview_users = db.relationship('User', secondary=tbl_set_trace_previews,
                                    backref=db.backref('preview_sets', lazy='dynamic'), lazy='dynamic')
    collection_users = db.relationship('User', secondary=tbl_set_trace_collections,
                                       backref=db.backref('collection_sets', lazy='dynamic'), lazy='dynamic')
    share_users = db.relationship('User', secondary=tbl_set_trace_shares,
                                  backref=db.backref('share_sets', lazy='dynamic'), lazy='dynamic')

    def getBaseJSON(self):
        return {
            'id': self.id,
            'name': self.name,
            'thumb': self.thumb,
            'url': self.url,
            'description': self.description,
            'create_time': format_datetime(self.create_time),

            'active': self.active,
            'copyright_protection': self.copyright_protection,
            'is_shield': self.is_shield,
            'is_removed': self.is_removed,

            'download_quantity': self.download_users.count(),
            'preview_quantity': self.preview_users.count(),
            'collection_quantity': self.collection_users.count(),
            'share_quantity': self.share_users.count()
        }

    def getJSON(self):
        """
        获取可JSON化的数据
        :return:
        """
        info = self.getBaseJSON()
        info.update({
            'tags_count': _Utils.auto_calc_count(self.tags),
            'categories_count': _Utils.auto_calc_count(self.categories),
            'items_count': _Utils.auto_calc_count(self.items),
        })
        return info

    def getJSONEx(self):
        info = self.getJSON()
        info.update({
            'tags': _Utils.calc_list(self.tags),
            'categories': _Utils.calc_list(self.categories),
            'items': _Utils.calc_list(self.items),
        })
        return info

    @staticmethod
    def get_items_order_by_set_id(_set_id=None):
        use_orm = False
        set_id = _set_id
        if use_orm:
            cur_set = Set.query.filter_by(id=set_id).first()
            query = None
            if cur_set:
                query = cur_set.items

            return query
        else:
            return db.session.query(Item,
                                    SetToItems.__table__.c.order,
                                    SetToItems.__table__.c.bewrite,
                                    SetToItems.__table__.c.active,
                                    SetToItems.__table__.c.copyright_protection,
                                    SetToItems.__table__.c.is_shield,
                                    SetToItems.__table__.c.is_removed,
                                    ).join(SetToItems.__table__,
                                           (SetToItems.__table__.c.set_id == set_id)).filter(
                SetToItems.__table__.c.item_id == Item.id) \
                .order_by(SetToItems.__table__.c.order.asc()).filter()


### 评论部分
class CommentsForItem(db.Model):
    """
    评论针对单个资源文件的
    """
    __tablename__ = constTablePrefix + 'comments_for_item'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'item.id'), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'user.id'), nullable=False)
    comment = db.Column(db.Text(12000), nullable=False)

    parent_id = db.Column(db.Integer, db.ForeignKey(__tablename__ + '.id'))  ## 针对的上一级评论

    is_shield = db.Column(db.Boolean, nullable=False, default=False, doc='是否被系统设置屏蔽')
    is_removed = db.Column(db.Boolean, nullable=False, default=False, doc='是否被标记移除')

    history = db.Column(db.Text(900000), nullable=False, default='', doc='历史记录，json数据类型')

    modify_time = db.Column(db.DateTime, default=datetime.utcnow)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


class CommentsForSet(db.Model):
    """
    评论针对资源素材包
    """

    __tablename__ = constTablePrefix + 'comments_for_set'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    set_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'set.id'), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'user.id'), nullable=False)
    comment = db.Column(db.Text(12000), nullable=False)

    parent_id = db.Column(db.Integer, db.ForeignKey(__tablename__ + '.id'))  ## 针对的上一级评论

    is_shield = db.Column(db.Boolean, nullable=False, default=False, doc='是否被系统设置屏蔽')
    is_removed = db.Column(db.Boolean, nullable=False, default=False, doc='是否被标记移除')

    history = db.Column(db.Text(900000), nullable=False, default='', doc='历史记录，json数据类型')

    modify_time = db.Column(db.DateTime, default=datetime.utcnow)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


"""
RelationShip
"""

## DataTypes
DataTypes.categories = db.relationship('Categories', backref='type', order_by=Categories.id)
DataTypes.tags = db.relationship('Tags', backref='type', order_by=Tags.id)

##See: https://stackoverflow.com/questions/6782133/sqlalchemy-one-to-many-relationship-on-single-table-inheritance-declarative
Categories.children = db.relationship('Categories', backref='parent', remote_side=Categories.id)
# Categories.tags = db.relationship('Tags', backref='category', order_by=Tags.id)

# CommentsForItem
CommentsForItem.children = db.relationship('CommentsForItem', backref='parent', remote_side=CommentsForItem.id)
CommentsForItem.item = db.relationship('Item', backref='comments', order_by=CommentsForItem.id)
CommentsForItem.user = db.relationship('User', backref='item_comments', order_by=CommentsForItem.id)

# CommentsForSet
CommentsForSet.children = db.relationship('CommentsForSet', backref='parent', remote_side=CommentsForSet.id)
CommentsForSet.set = db.relationship('Set', backref='comments', order_by=CommentsForSet.id)
CommentsForSet.user = db.relationship('User', backref='set_comments', order_by=CommentsForSet.id)
