#!/usr/bin/env python
# -*- coding: utf-8 -*-

from api.core.database import db
from uuid import uuid5
from datetime import datetime


def getNewUUID():
    return uuid5().hex()


class User(db.Model):
    '''
    全局用户表
    '''
    __tablename__ = 'users'

    id = db.Column(db.String(255), primary_key=True, default=getNewUUID, doc='唯一ID')
    name = db.Column(db.String(255), nullable=False, doc='数据类型的名称')
    description = db.Column(db.String(400), nullable=False, doc='数据类型的描述')

    create_time = db.Column(db.DateTime)


class Machines(db.Model):
    '''
    全局机器码表，作为跟踪用户的唯一标记
    '''
    __tablename__ = 'machines'

    id = db.Column(db.String(255), primary_key=True, doc='唯一ID') # 存储真实的机器码
    os = db.Column(db.String(20), default='MacOSX')
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


class UserMachines(db.Model):
    '''
    用户与机器码绑定关系， 1 对 多
    '''

    __tablename__ = 'users_machines'

    id = db.Column(db.Integer, db.Sequence(__tablename__ + '_id_seq'), autoincrement=True, default=1, primary_key=True, doc='唯一ID')
    user_id = db.Column(db.String(255), db.ForeignKey('users.id'), nullable=False)
    machine_id = db.Column(db.String(255), db.ForeignKey('machines.id'), nullable=False)