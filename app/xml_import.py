# -*- coding: utf-8 -*-
import sys
import os

from lxml import etree


reload(sys)
sys.setdefaultencoding("utf-8")
from app import app, db
from app.models import Category, Product, CategoryProduct, get_or_create
from app.utils import get_categories_tree
from datetime import datetime

prodCount = 0
existed = 0
category_pos = 0


def del_empty_categories(categories=get_categories_tree()):
    for category in categories:
        if category.children:
            del_empty_categories(category.children)
        elif len(CategoryProduct.query.filter(CategoryProduct.category_id == category.id).all()) == 0:
            q = Category.query.filter(Category.id == category.id)
            print "Remove category", q.one().name
            q.delete()
            db.session.commit()


def parseProduct(node, category_id):
    global existed
    _id = int(node.attrib["id"])
    product = get_or_create(db.session, Product, id=_id)
    product.name = node.attrib["name"]
    try:
        product.art = node.attrib["art"]
    except:
        product.art = ""
    product.exist = ''
    if node.attrib["nala"] != "0":
        product.exist += 'A '
    if node.attrib["nalb"] != "0":
        product.exist += 'Б '
    if node.attrib["nalk"] != "0":
        product.exist += 'К'
    product.exist = product.exist.strip()
    product.price = float(node.attrib["cena"])
    product.price_dk = float(node.attrib["skid"])
    try:
        product.link = node.attrib["opis"]
    except:
        pass
    try:
        product.icon = node.attrib["icon"]
    except:
        pass
    db.session.add(product)
    catprod = CategoryProduct(category_id, _id)
    existed += (product.exist != '')
    db.session.add(catprod)


def parseCategory(elem, level):
    global category_pos
    _id = int(elem.attrib["id"])
    _id += (level * 1000)
    category = get_or_create(db.session, Category, id=_id)
    category.name = elem.attrib["name"].rstrip()
    category.position = category_pos
    if level == 0:
        category.parent_id = 0
    else:
        category.parent_id = int(elem.getparent().attrib["id"])
        category.parent_id += ((level - 1) * 1000)
    category_pos += 1
    db.session.add(category)
    # remove all products from this category
    CategoryProduct.query.filter(CategoryProduct.category_id == _id).delete()
    db.session.commit()
    return category


def parse(context, parentCategory=None):
    """Parse XML file by SAX"""
    global prodCount, existed
    count = 0
    level = -1
    for action, elem in context:
        if elem.tag in ["GRMATER", "SGRMAT", "TOBE"]:
            if action == "start":
                level += 1
                category = parseCategory(elem, level)
            else:
                if elem.tag == "TOBE":
                    category.existed_products = existed
                    existed = 0
                    print str(elem.attrib["name"]) + u", товаров: " + str(prodCount - count)
                count = prodCount
                level -= 1
                db.session.commit()
        elif action == "end" and elem.tag == "OBE":
            parseProduct(elem, category.id)
            prodCount += 1


def xml_import():
    start = datetime.now()
    print "Parsing XML..."
    if not os.path.exists("price_cmpt.xml"):
        raise Exception("File price_cmpt.xml not exist")
    db.create_all()
    try:
        parse(etree.iterparse("price_cmpt.xml", events=("start", "end",), encoding="cp1251"))
        db.session.commit()
    except Exception, ex:
        print ex
    print "Finished"
    print "Elapsed:", str(datetime.now() - start), "sec for import", str(prodCount), "products"
    if prodCount:
        print (datetime.now() - start) / prodCount, "sec/product"


app.xml_import = xml_import

