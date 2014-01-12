# -*- coding: utf-8 -*-
from functools import wraps
import os
from datetime import datetime
from flask.globals import request

from app.models import Category, CategoryProduct
from app import app, cache
from config import USER_IMG_DIR


def stripped(x):
    return "".join(c for c in x if ord(c) >= 32)


def contains_digits(s):
    return any(char.isdigit() for char in s)


def get_categories_tree(parent_id=0, level=0):
    categories = Category.query.filter(Category.parent_id == parent_id).order_by(Category.position).all()
    if level < 2:
        for c in categories:
            c.children = get_categories_tree(c.id, level + 1)
    else:
        for c in categories:
            c.products_count = CategoryProduct.query.filter(CategoryProduct.category_id == c.id).count()

    return categories


def get_categories():
    categories = cache.get('categories')
    if not categories:
        categories = get_categories_tree()
        cache.set('categories', categories, 24 * 3600)
    return categories#get_categories_tree()#categories


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = datetime.now()
        out = func(*args, **kwargs)
        print func.__name__, datetime.now() - start
        return out

    return wrapper


def memoize(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = 'memo' + request.path + str(request.form.values())
        key = key.translate(dict.fromkeys(range(33)))
        output = cache.get(key)
        if output is None:
            output = func(*args, **kwargs)
            cache.set(key, output, 3600)
        return output

    return wrapper


def format_currency(value):
    return ("%.2F" % value).replace(".", ".")


app.jinja_env.filters['format_currency'] = format_currency


def gen_images_list():
    # [{"image":"/static/img/logo.bmp"},{"image":"/static/img/excel.png"}]
    with open(os.path.join(USER_IMG_DIR, 'images_list.json'), 'wt') as json:
        json.write('[')
        for name in os.listdir(USER_IMG_DIR):
        #            if name.endswith('.jpg'):
            json.write('{"image":"/static/upload/img/' + name + '"},')
        json.write('{}]')
