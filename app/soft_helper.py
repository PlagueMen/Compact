# -*- coding: utf-8 -*-
import csv
from operator import itemgetter
import re

from app.models import Product, SoftServiceProduct, get_or_create, delete_if_enable
from app import db


__author__ = 'Alex'


def read_csv():
    with open('app/static/upload/softservice.csv', 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')
        for row in spamreader:
            sid = row[0].decode("cp1251")
            ssp = get_or_create(db.session, SoftServiceProduct, soft_id=sid)
            try:
                ssp.price = float(row[1])
            except:
                pass
            ssp.name = row[2].decode("cp1251")
            db.session.add(ssp)
    delete_if_enable(db.session, SoftServiceProduct, name="name")
    db.session.commit()
    return True


def search_product(name, filter_text):
    words = re.findall(u'[А-ЯA-Z]+|[0-9]+', name.upper())
    res = []
    print filter_text
    products = Product.query.filter((Product.name.match(name)) & (
        (Product.name.like("%" + filter_text + "%")) | (Product.art.like("%" + filter_text + "%")))).all()
    print len(products)
    for product in products:
        count = 0
        name_words = re.findall(u'[А-ЯA-Z]+|[0-9]+', product.name.upper())
        for word in words:
            if len(word) == 0:
                continue
            if word in name_words:
                count += 1
        if count > 0:
            res.append((product, count))
    res = sorted(res, key=itemgetter(1), reverse=True)[:20]
    return [x[0] for x in res]


def set_soft_id(index, cmpt_id):
    product = SoftServiceProduct.query.get(index)
    product.cmpt_id = cmpt_id
    db.session.add(product)
    db.session.commit()


def import_products(text):
    try:
        for line in text.splitlines():
            line = line.split()
            product = SoftServiceProduct.query.filter(SoftServiceProduct.soft_id == line[0].upper()).one()
            if product is not None:
                product.cmpt_id = int(line[1])
                print product.cmpt_id
                db.session.add(product)
    except:
        return False
    return True


def export_products():
    res = ''
    for item in SoftServiceProduct.query.filter(SoftServiceProduct.cmpt_id != 0).all():
        res = ''.join([res, str(item), '<br>'])
    return res