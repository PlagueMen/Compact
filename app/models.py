# -*- coding: utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
from app import db
from flask.ext.login import UserMixin

ROLE_USER = 0
ROLE_MANAGER = 1
ROLE_ADMIN = 2


class Filter:
    exist_a = False
    exist_b = False
    exist_k = False
    exist = True
    exist_all = False
    low = 0
    high = 999999
    filter = ''


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        return instance


def delete_if_enable(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        session.delete(instance)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    parent_id = db.Column(db.Integer)
    position = db.Column(db.Integer)
    existed_products = db.Column(db.Integer)
    active = False
    children = []

    categoryproduct = db.relationship('CategoryProduct', passive_deletes=True)

    def __init__(self, id, name='unknown', level=0, parent_id=0, position=0):
        self.id = id
        self.name = name
        self.level = level
        self.parent_id = parent_id
        self.position = position
        self.children = None

    def __repr__(self):
        return '<Category: (%s, %s)>' % (self.id, self.name)


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    art = db.Column(db.String(90))
    price = db.Column(db.Float)
    price_dk = db.Column(db.Float)
    exist = db.Column(db.String(10))
    link = db.Column(db.String(200))
    icon = db.Column(db.String(200))
    categoryprouct = db.relationship('CategoryProduct', passive_deletes=True)

    def __init__(self, id, name='unknown', art=None, price=0.0, price_dk=0.0, exist='', link=None, icon=None):
        self.id = id
        self.name = name
        self.art = art
        self.price = price
        self.price_dk = price_dk
        self.exist = exist
        self.link = link
        self.icon = icon

    def __unicode__(self):
        return self.name


class CategoryProduct(db.Model):
    __tablename__ = 'categoryproduct'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))

    def __init__(self, category_id, product_id):
        self.category_id = category_id
        self.product_id = product_id


class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(80))
    active = db.Column(db.Boolean, default=True)
    description = db.Column(db.String(500))
    text = db.Column(db.UnicodeText(5000))
    creation_date = db.Column(db.Date)

    def __unicode__(self):
        return self.title


class Partner(db.Model):
    __tablename__ = 'partners'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    active = db.Column(db.Boolean, default=True)
    logo = db.Column(db.UnicodeText(80))
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.UnicodeText(5000))

    def __unicode__(self):
        return self.name


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(20))
    first_name = db.Column(db.String(50))
    second_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(10))
    discont = db.Column(db.Integer)
    role = db.Column(db.SmallInteger, default=ROLE_USER)

    def __unicode__(self):
        return self.email


class SoftServiceProduct(db.Model):
    __tablename__ = "softservice"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    soft_id = db.Column(db.String(12), unique=True)
    price = db.Column(db.Float())
    cmpt_id = db.Column(db.Integer, default=0)
    name = db.Column(db.String(200))

    def __str__(self):
        return u''.join([str(self.soft_id), ' ', str(self.cmpt_id)])
