#!/usr/bin/env python
# -*- coding: utf-8 -*-

# system package
from datetime import datetime

# libs
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm.collections import attribute_mapped_collection

# project
from api.gmagon.database import db
from api.gmagon.plugins.gif.util import constTablePrefix, format_datetime


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
    thumb = db.Column(db.String(255), default='')
    description = db.Column(db.String(400), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'types.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'categories.id'), nullable=True)

    def getJSON(self):
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


class Tags(db.Model):
    '''
    资源基础数据标签（全局类型）
    '''

    __tablename__ = constTablePrefix + 'tags'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    thumb = db.Column(db.String(255), default='')
    description = db.Column(db.String(400), nullable=False)
    category_id = db.Column(db.ForeignKey(constTablePrefix + 'categories.id'))
    type_id = db.Column(db.ForeignKey(constTablePrefix + 'types.id'), nullable=False)

    def getJSON(self):
        return {
            'id': self.id,
            'name': self.name,
            'thumb': self.thumb,
            'description': self.description,
            'category_id': self.category_id,
            'category_name': self.category.name,
            'type_id': self.type_id,
            'type_name': self.type.name
        }


### 用户部分
tbl_followers = db.Table(constTablePrefix + 'followers',
                         db.Column('follower_id', db.Integer, db.ForeignKey(constTablePrefix + 'user.id')),
                         db.Column('followed_id', db.Integer, db.ForeignKey(constTablePrefix + 'user.id'))
                         )


class User(db.Model):
    '''
    资源专区的用户
    '''
    __tablename__ = constTablePrefix + 'user'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联的机器码
    machine_id = db.Column(db.String(255), db.ForeignKey('machines.id'), doc='唯一ID')  # 存储真实的机器码
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


'''
Many-to-Many Relationships
'''
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

'''下载
'''
tbl_item_trace_downloads = db.Table(constTablePrefix + 'trace_item_downloads',
                                    db.Column('id', db.Integer,
                                              db.Sequence(constTablePrefix + 'trace_item_downloads' + '_id_seq'),
                                              autoincrement=True, primary_key=True),
                                    db.Column('item_id', db.ForeignKey(constTablePrefix + 'item.id'), nullable=False),
                                    db.Column('user_id', db.ForeignKey(constTablePrefix + 'user.id'), nullable=False),
                                    db.Column('createtime', db.DateTime, default=datetime.utcnow)
                                    )
'''浏览，类似于试听
'''
tbl_item_trace_previews = db.Table(constTablePrefix + 'trace_item_previews',
                                   db.Column('id',db.Integer,
                                             db.Sequence(constTablePrefix + 'trace_item_previews' + '_id_seq'),
                                             autoincrement=True, primary_key=True),
                                   db.Column('item_id', db.ForeignKey(constTablePrefix + 'item.id'), nullable=False),
                                   db.Column('user_id', db.ForeignKey(constTablePrefix + 'user.id'), nullable=False),
                                   db.Column('create_time', db.DateTime, default=datetime.utcnow)
                                   )

'''收藏
'''
tbl_item_trace_collections = db.Table(constTablePrefix + 'trace_item_collections',
                                      db.Column('id',db.Integer,
                                                db.Sequence(constTablePrefix + 'trace_item_collections' + '_id_seq'),
                                                autoincrement=True, primary_key=True),
                                      db.Column('item_id', db.ForeignKey(constTablePrefix + 'item.id'), nullable=False),
                                      db.Column('user_id', db.ForeignKey(constTablePrefix + 'user.id'), nullable=False),
                                      db.Column('create_time', db.DateTime, default=datetime.utcnow)
                                      )
'''分享
'''
tbl_item_trace_shares = db.Table(constTablePrefix + 'trace_item_shares',
                                 db.Column('id',db.Integer, db.Sequence(constTablePrefix + 'trace_item_shares' + '_id_seq'),
                                           autoincrement=True, primary_key=True),
                                 db.Column('item_id', db.ForeignKey(constTablePrefix + 'item.id'), nullable=False),
                                 db.Column('user_id', db.ForeignKey(constTablePrefix + 'user.id'), nullable=False),
                                 db.Column('create_time', db.DateTime, default=datetime.utcnow)
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

    '''Relations
    '''
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

        download_quantity = self.download_users.count()  # '被下载的次数'
        preview_quantity = self.preview_users.count()  # '被浏览的次数'
        collection_quantity = self.collection_users.count()  # '被收藏的次数'
        share_quantity = self.share_users.count()  # 被分享的次数'

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

            'download_quantity': download_quantity,
            'preview_quantity': preview_quantity,
            'collection_quantity': collection_quantity,
            'share_quantity': share_quantity,

            'tags': tagsDataList,
            'categories': categoriesDataList
        }

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


'''
Many-to-Many Relationships
'''
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
tbl_set_items = db.Table(constTablePrefix + 'set_items',
                         db.Column('set_id', db.ForeignKey(constTablePrefix + 'set.id'), nullable=False,
                                   primary_key=True),
                         db.Column('item_id', db.ForeignKey(constTablePrefix + 'item.id'), nullable=False,
                                   primary_key=True),
                         db.Column('order', db.Integer, nullable=False, default=0, doc='排序'),
                         db.Column('active', db.Boolean, nullable=False, default=True, doc='数据项是否处于激活状态，激活即为可用'),
                         db.Column('copyright_protection', db.Boolean, nullable=False, default=False,
                                   doc='数据项是否处于版权保护'),
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
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    active = db.Column(db.Boolean, nullable=False, default=True, doc='数据项是否处于激活状态，激活即为可用')
    copyright_protection = db.Column(db.Boolean, nullable=False, default=False, doc='数据项是否处于版权保护')
    is_shield = db.Column(db.Boolean, nullable=False, default=False, doc='是否被系统设置屏蔽')
    is_removed = db.Column(db.Boolean, nullable=False, default=False, doc='是否被标记移除')

    download_quantity = db.Column(db.Integer, default=0, nullable=False, doc='被下载的次数')
    preview_quantity = db.Column(db.Integer, default=0, nullable=False, doc='被浏览的次数')
    collection_quantity = db.Column(db.Integer, default=0, nullable=False, doc='被收藏的次数')
    share_quantity = db.Column(db.Integer, default=0, nullable=False, doc='被分享的次数')

    tags = db.relationship('Tags', secondary=tbl_set_tags,
                           primaryjoin=id == tbl_set_tags.c.set_id,
                           backref=db.backref('sets', lazy='dynamic'), lazy='dynamic')
    categories = db.relationship('Categories', secondary=tbl_set_categories,
                                 primaryjoin=id == tbl_set_categories.c.set_id,
                                 backref=db.backref('sets', lazy='dynamic'), lazy='dynamic')
    items = db.relationship('Item', secondary=tbl_set_items,
                            primaryjoin=(id == tbl_set_items.c.set_id),
                            order_by=tbl_set_items.c.order,
                            # collection_class=ordering_list('order'),
                            collection_class=attribute_mapped_collection('order'),
                            backref=db.backref('sets', lazy='dynamic'), lazy='dynamic')

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

        item_data_list = []
        for item in self.items:
            ele = item.getJSON()
            item_data_list.append(ele)

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

            'download_quantity': self.download_quantity,
            'preview_quantity': self.preview_quantity,
            'collection_quantity': self.collection_quantity,
            'share_quantity': self.share_quantity,

            'tags': tagsDataList,
            'categories': categoriesDataList,
            'items': item_data_list

        }

    @staticmethod
    def sort_sets_by_tag_id(tag_id):
        cur_tag = Tags.query.filter_by(id=tag_id)
        return cur_tag.sets
        # return Set.query.join(tbl_set_tags,
        #                        (tbl_set_tags.c.tag_id == tag_id)).filter(tbl_set_tags.c.set_id == Set.id)\
        #     .order_by(Set.id.desc()).filter()

    @staticmethod
    def sort_sets_by_category_id(category_id):
        return Set.query.join(tbl_set_categories,
                              (tbl_set_categories.c.category_id == category_id)).filter(
            tbl_set_categories.c.set_id == Set.id) \
            .order_by(Set.id.desc()).filter()

    @staticmethod
    def sort_items_by_set_id0(set_id):
        return Item.query.join(tbl_set_items,
                               (tbl_set_items.c.set_id == set_id)).filter(tbl_set_items.c.set_id == Set.id) \
            .filter(tbl_set_items.c.item_id == Item.id) \
            .order_by(tbl_set_items.c.order.asc()).filter()

    @staticmethod
    def sort_items_by_set_id(set_id):
        cur_set = Set.query.filter_by(id=set_id).first()
        if cur_set:
            return cur_set.items

        return None


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

    modify_time = db.Column(db.DateTime, default=datetime.utcnow)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


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

    modify_time = db.Column(db.DateTime, default=datetime.utcnow)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


class UserTrace(db.Model):
    '''
    针对用户的操作跟踪，为后面分析用户行为及数据做准备
    '''

    __tablename__ = constTablePrefix + 'user_trace'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'user.id'), nullable=False)
    type = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'types.id'), nullable=False)
    content = db.Column(db.Text, nullable=False, default='')
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


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

    create_time = db.Column(db.DateTime, default=datetime.utcnow)


class UserAnalysisAUTO(db.Model):
    '''
    根据用户的习惯（从用户的行为中分析得来），推荐给用户一些自动化的信息
    '''
    __tablename__ = constTablePrefix + 'user_analysis_auto'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='分析谁')
    type = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'types.id'), nullable=False, doc='分析的数据类型')
    content = db.Column(db.Text, nullable=False, default='', doc='分析的结果')

    create_time = db.Column(db.DateTime, default=datetime.utcnow)


class TraceSetDownload(db.Model):
    '''
    跟踪资源素材包的下载情况
    '''
    __tablename__ = constTablePrefix + 'trace_set_download'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)

    set_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'set.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='谁')
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


class TraceSetPreview(db.Model):
    '''
    跟踪资源素材包的浏览情况
    '''
    __tablename__ = constTablePrefix + 'trace_set_preview'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)

    set_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'set.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='谁')
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


class TraceSetCollection(db.Model):
    '''
    跟踪资源素材包的收藏情况
    '''
    __tablename__ = constTablePrefix + 'trace_set_collection'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)

    set_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'set.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='谁')
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


class TraceSetShare(db.Model):
    '''
    跟踪资源素材包的收藏情况
    '''
    __tablename__ = constTablePrefix + 'trace_set_share'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, primary_key=True)

    set_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'set.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(constTablePrefix + 'user.id'), nullable=False, doc='谁')
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


'''
RelationShip
'''

## DataTypes
DataTypes.categories = db.relationship('Categories', backref='type', order_by=Categories.id)
DataTypes.tags = db.relationship('Tags', backref='type', order_by=Tags.id)

##See: https://stackoverflow.com/questions/6782133/sqlalchemy-one-to-many-relationship-on-single-table-inheritance-declarative
Categories.children = db.relationship('Categories', backref='parent', remote_side=Categories.id)
Categories.tags = db.relationship('Tags', backref='category', order_by=Tags.id)

# CommentsForItem
CommentsForItem.children = db.relationship('CommentsForItem', backref='parent', remote_side=CommentsForItem.id)
CommentsForItem.item = db.relationship('Item', backref='comments', order_by=CommentsForItem.id)

# CommentsForSet
CommentsForSet.children = db.relationship('CommentsForSet', backref='parent', remote_side=CommentsForSet.id)
CommentsForSet.set = db.relationship('Set', backref='comments', order_by=CommentsForSet.id)
