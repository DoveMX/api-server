#!/usr/bin/env python
# -*- coding: utf-8 -*-

from api.gmagon.database import db
from uuid import uuid4
from datetime import datetime

def retain():
    return True

def getNewUUID():
    return uuid4().hex


constSchema = 'GLOB'

class GUser(db.Model):
    '''
    全局用户表
    '''
    __tablename__ = 'users'

    id = db.Column(db.String(255), default=getNewUUID, primary_key=True, doc='唯一ID')
    name = db.Column(db.String(255), nullable=False, doc='数据类型的名称')
    description = db.Column(db.String(400), nullable=False, doc='数据类型的描述')

    create_time = db.Column(db.DateTime, default=datetime.utcnow)




class GUserMachines(db.Model):
    '''
    全局机器码表，作为跟踪用户的唯一标记
    '''
    __tablename__ = 'machines'

    id = db.Column(db.String(255), primary_key=True, doc='唯一ID') # 存储真实的机器码
    os = db.Column(db.String(20), default='MacOSX')

    user_id = db.Column(db.ForeignKey('users.id'), nullable=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


## 创建关系
GUser.machines = db.relationship('GUserMachines', backref='user', order_by=GUserMachines.id)