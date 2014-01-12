# -*- coding: cp1251 -*-
from datetime import datetime, date

import xlwt

from app.models import CategoryProduct, Product
from app.utils import get_categories

style0 = xlwt.easyxf("font: name Arial, height 320, color-index black; align: vert centre, horiz center;")
style1 = xlwt.easyxf("font: name Arial,height 200, color-index black; align: vert centre, horiz center;")
styleRow = xlwt.easyxf(
    "font: name Arial, colour_index black; align: wrap on, vert centre, horiz center;"      "borders: top thin, bottom thin, left thin, right thin;")
styleRowL = xlwt.easyxf(
    "font: name Arial, colour_index black; align: wrap on, vert centre, horiz left;"      "borders: top thin, bottom thin, left thin, right thin;")
styleHeader = xlwt.easyxf(
    "font: name Arial, colour_index black, bold on; align: wrap on, vert centre, horiz left;"      "borders: top thin, bottom thin, left thin, right thin;")

row = 6


def write_products(sheet, products, level):
    global row
    for p in products:
        sheet.write(row, 0, p.id, styleRow)
        sheet.write(row, 1, p.name, styleRowL)
        sheet.write(row, 2, p.art, styleRow)
        sheet.write(row, 3, p.price, styleRow)
        sheet.write(row, 4, "V" if (u'А' in p.exist) else "", styleRow)
        sheet.write(row, 5, "V" if (u'Б' in p.exist) else "", styleRow)
        sheet.write(row, 6, "V" if (u'К' in p.exist) else "", styleRow)
        sheet.row(row).level = level
        sheet.row(row).hidden = 1
        sheet.row(row).height = len(p.name) * 15
        sheet.row(row).height_mismatch = 1
        row += 1


def write_category(sheet, categories, level=0):
    global row
    for category in categories:
        sheet.write_merge(row, row, 0, 6, "    " * level + category.name, styleHeader)
        sheet.row(row).level = level
        sheet.row(row).hidden = level > 0
        sheet.row(row).collapse = 1
        sheet.row(row).height = 330
        row += 1
        if level == 0:
            print category.name
        sq = CategoryProduct.query.filter(CategoryProduct.category_id == category.id).subquery()
        products = Product.query.filter(sq.c.product_id == Product.id).order_by(Product.exist.desc())
        write_products(sheet, products, level + 1)
        write_category(sheet, category.children, level + 1)


def write_sheets(book, categories):
    global row
    for category in categories:
        ws = book.add_sheet(category.name, True)
        ws.col(0).width = 10 * 200
        ws.col(1).width = 50 * 200
        ws.col(2).width = 20 * 200
        ws.col(3).width = 9 * 200
        ws.col(4).width = 15 * 200
        ws.col(5).width = 9 * 200
        ws.col(6).width = 10 * 200

        ws.row(0).height = 350
        ws.row(1).height = 280
        ws.row(2).height = 250
        ws.row(3).height = 250
        ws.row(4).height = 350
        ws.row(5).height = 350

        ws.write_merge(1, 1, 0, 4, u"Прайс-лист фирмы «Компакт» от %sг." % date.today(), style0)
        ws.write_merge(2, 2, 0, 4, u"При безналичном расчете +3%, более полная информация на http://компакт.рф", style1)
        ws.write_merge(3, 3, 0, 4, u"тел./факс (47234) 4-62-02 (многоканальный)", style1)
        ws.write_merge(4, 5, 0, 0, u"Код", styleRow)
        ws.write_merge(4, 5, 1, 1, u"Наименование", styleRow)
        ws.write_merge(4, 5, 2, 2, u"Артикул", styleRow)
        ws.write_merge(4, 5, 3, 3, u"Цена, руб.", styleRow)
        ws.write_merge(4, 4, 4, 6, u"Наличие", styleRow)
        ws.write(5, 4, u"Алексеевка", styleRow)
        ws.write(5, 5, u"Бирюч", styleRow)
        ws.write(5, 6, u"Красное", styleRow)
        row = 6
        write_category(ws, category.children)
        ws.write_merge(row + 2, row + 2, 0, 6,
                       u"Это прайс-лист на %s," % category.name,
                       styleHeader)
        ws.write_merge(row + 3, row + 3, 0, 6, u"остальные товары Вы можете увидеть на других листах документа",
                       styleHeader)


def generate_price(logo_path, price_path):
    print "Generate price"
    start = datetime.now()
    wb = xlwt.Workbook()
    write_sheets(wb, get_categories())
    wb.save(price_path)
    print "Price generated at", str(datetime.now() - start), "sec"
