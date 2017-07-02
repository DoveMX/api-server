#!/usr/bin/env python
# -*- coding: utf-8 -*-

# system
from uuid import uuid4
from datetime import datetime
import re

# lib
from flask_login import UserMixin

# local
from api.gmagon.database import db


def retain():
    return True


def getNewUUID():
    return uuid4().hex


constSchema = 'GLOB'

# 构建查看其他源码参照: https://github.com/lefttree/flaskApp/blob/master/app/models.py
# Note: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-ix-pagination

class GUser(UserMixin, db.Model):
    '''
    全局用户表
    '''
    __tablename__ = 'users'

    id = db.Column(db.String(255), default=getNewUUID, primary_key=True, doc='唯一ID')
    social_id = db.Column(db.String(64), nullable=False, unique=True, doc="社交ID")
    nickname = db.Column(db.String(64), nullable=False, index=True, unique=True, doc="昵称")
    email = db.Column(db.String(120), nullable=True, index=True, unique=True, doc="email地址")
    avatarLarge = db.Column(db.String, nullable=True, index=True, unique=True, doc="头像大")
    avatarSmall = db.Column(db.String, nullable=True, index=True, unique=True, doc="头像小")
    about_me = db.Column(db.String(140), doc="关于我")
    last_seen = db.Column(db.DateTime, doc="最近登录时间")
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def make_unique_nickname(nickname):
        if GUser.query.filter_by(nickname=nickname).first() is None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if GUser.query.filter_by(nickname=new_nickname).first() is None:
                break
            version += 1
        return new_nickname


    @staticmethod
    def make_valid_nickname(nickname):
        return re.sub('[^a-zA-Z0-9_\.\s]', '', nickname)


class GUserMachines(db.Model):
    '''
    全局机器码表，作为跟踪用户的唯一标记
    '''
    __tablename__ = 'machines'

    id = db.Column(db.String(255), primary_key=True, doc='唯一ID')  # 存储真实的机器码
    os = db.Column(db.String(20), default='MacOSX')

    user_id = db.Column(db.ForeignKey('users.id'), nullable=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


## 创建关系
GUser.machines = db.relationship('GUserMachines', backref='user', order_by=GUserMachines.id)
