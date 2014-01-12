# -*- coding: utf-8 -*-
import datetime

from flask import render_template, flash, redirect, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user
from flask.templating import render_template_string

from app import app, db, lm
from app.soft_helper import search_product, set_soft_id, read_csv, export_products, import_products
from app.utils import gen_images_list, memoize, timer
from models import User, CategoryProduct, Product, Category
from utils import get_categories, contains_digits
from app.models import Filter, News, Partner, SoftServiceProduct


@app.route('/')
@app.route('/index')
def index():
    gen_images_list()
    return render_template("home.html")


@lm.user_loader
def load_user(email):
    return User.query.get(email)


@app.before_request
def before_request():
    g.user = current_user


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user and g.user.is_authenticated():
        return redirect(url_for('index'))
    if request.method == "POST":
        user = User.query.filter(User.email == request.form["email"].strip()).first()
        if user is None:
            return render_template("login.html",
                                   email_error="Пользователь с данным адресом электронной почты не зарегистрирован в системе")
        if user.password != request.form["password"].strip():
            return render_template("login.html",
                                   password_error="Неверный пароль, проверьте адрес электронной почты и пароль")
        else:
            login_user(user, remember=("remember_me" in request.form))
            flash("Вы успешно вошли")
            return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = User()
        user.email = request.form["email"].strip()
        user.password = request.form["password"].strip()
        user.name = request.form["name"].strip()
        user.second_name = request.form["second_name"].strip()
        user.last_name = request.form["last_name"].strip()
        user.phone = request.form["phone"].strip()
        user.discont = request.form["discont"].strip()
        if User.query.filter(User.email == user.email).count() > 0:
            return render_template("register.html", email_error="Этот адрес уже занят", user=user)
        if len(user.password) < 3:
            return render_template("register.html",
                                   password_error="Длина пароля должна быть минимум 3 символа (буквы, цифры)",
                                   user=user)
        if contains_digits(user.name):
            return render_template("register.html", name_error="В человеческом имени не может быть цифр", user=user)
        if contains_digits(user.second_name):
            return render_template("register.html", second_name_error="В человеческой фамилии не может быть цифр",
                                   user=user)
        if contains_digits(user.last_name):
            return render_template("register.html", last_name_error="В человеческом отчестве не может быть цифр",
                                   user=user)
        if user.phone and len(user.phone) != 10:
            return render_template("register.html",
                                   phone_error="Номер телефона должен должен быть 10-значным, вида 9XXXXXXX", user=user)
        if user.discont and len(user.discont) != 8:
            return render_template("register.html", discont_error="Номер дисконтной карты должен быть 8-значным",
                                   user=user)
        if not "accept" in request.form:
            return render_template("register.html",
                                   accept_error="Чтобы зарегистрироваться, ознакомьтесь с условиями и подтвердите свое согласие",
                                   user=user)
        db.session.add(user)
        db.session.commit()
        flash("Вы успешно зарегистрированы на сайте")
        return redirect(url_for("login"))
    return render_template("register.html", user=User())


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/code-<index>')
def code(index):
    return Product.query.get(index).name


@app.route("/category-<index>", methods=["GET", "POST"])
@timer
@memoize
def category(index):
    try:
        category_title = Category.query.get(index).name
    except:
        print "Error: no catalog with id", index
        return

    sq = CategoryProduct.query.filter(CategoryProduct.category_id == index).subquery()
    products = Product.query.filter(sq.c.product_id == Product.id)
    _filter = Filter()
    if request.method == "POST":
        if request.form.has_key("exist"):
            _filter.exist = request.form["exist"] == "exist"
            _filter.exist_a = request.form["exist"] == "exist_a"
            _filter.exist_b = request.form["exist"] == "exist_b"
            _filter.exist_k = request.form["exist"] == "exist_k"
            _filter.exist_all = request.form["exist"] == "exist_all"
        if request.form["price_low"]:
            _filter.low = request.form["price_low"]
            products = products.filter(Product.price > _filter.low)
        if request.form["price_high"]:
            _filter.high = request.form["price_high"]
            products = products.filter(Product.price < _filter.high)
        if request.form["filter"]:
            _filter.filter = request.form["filter"]
            words = _filter.filter.split()
            products = products.filter(Product.name.like("%" + words[0] + "%"))
            for word in words[1:]:
                products = products.filter(Product.name.like("%" + word + "%"))

    if not _filter.exist_all:
        if _filter.exist:
            products = products.filter(Product.exist != '')
        elif _filter.exist_a:
            products = products.filter(Product.exist.like('%A%'))
        elif _filter.exist_b:
            products = products.filter(Product.exist.like('%Б%'))
        elif _filter.exist_k:
            products = products.filter(Product.exist.like('%К%'))

    products = products.order_by(Product.exist).all()
    products = sorted(products, key=lambda product: len(product.exist), reverse=True)
    g.date = datetime.date.today()

    return render_template("products.html", products=products, categories=get_categories(),
                           category_title=category_title, filter=_filter)


#@app.route("/search", methods=["GET", "POST"])
#@memoize
def search1():
    g.date = datetime.date.today()
    if request.method == "POST":
        data = request.form["search"]
        try: # try to display product by id
            _id = int(data)
            product = Product.query.filter(Product.id == _id).one()
            cat_prod = CategoryProduct.query.filter(CategoryProduct.product_id == product.id).one()
            category = Category.query.get(cat_prod.category_id)
            return render_template("search.html", products=[product], category_title=category.name, search=data)
        except:
            pass

        words = data.split()
        products = Product.query.filter(Product.name.like("%" + words[0] + "%"))
        for word in words[1:]:
            products = products.filter(Product.name.like("%" + word + "%"))
            #products = products.order_by(Product.exist.desc()).all()
        products = products.all()
        return render_template("search.html", products=products[:50], category_title="Результаты поиска",
                               count=len(products), search=data)
    return redirect(url_for('index'))


@app.route("/search", methods=["GET", "POST"])
@memoize
def search():
    g.date = datetime.date.today()
    if request.method == "POST":
        data = request.form["search"]
        try: # try to display product by id
            _id = int(data)
            product = Product.query.filter(Product.id == _id).one()
            cat_prod = CategoryProduct.query.filter(CategoryProduct.product_id == product.id).one()
            category = Category.query.get(cat_prod.category_id)
            return render_template("search.html", products=[product], category_title=category.name, search=data)
        except:
            pass

        products = Product.query.filter(Product.name.match(data)).all()
        return render_template("search.html", products=products[:50], category_title="Результаты поиска",
                               count=len(products), search=data)
    return redirect(url_for('index'))


@app.route("/catalog")
@memoize
def catalog():
    return render_template("catalog.html", categories=get_categories())


@app.route("/news")
def news_list():
    _news = News.query.filter(News.active).all()
    return render_template("news.html", news=_news)


@app.route("/news-<index>")
def news(index):
    _new = News.query.filter(News.id == index).one()
    return render_template("new.html", new=_new)


@app.route("/partners")
def partners():
    return render_template("partners.html", partners=Partner.query.all())


@app.route("/partner-<index>")
def partner(index):
    return render_template("partner.html", partner=Partner.query.filter(Partner.id == index).one())


@app.route("/price_list")
def price_list():
    return render_template("price_list.html")


@app.route("/contacts")
def contacts():
    return render_template("contacts.html")


@app.route("/about")
def about():
    return render_template("about.html")


products = None


@app.route("/soft", methods=["GET", "POST"])
@timer
def soft():
    showall = False
    if request.method == "POST":
        if "load_list" in request.form:
            if read_csv():
                flash(u"Список товаров успешно загружен")
        if "show_all" in request.form:
            showall = True
        if "show_no" in request.form:
            showall = False
        if "export_products" in request.form:
            return render_template_string(export_products())
        if "import_products" in request.form:
            if import_products(request.form["text"]):
                flash(u"Список товаров успешно обработан")
            else:
                flash(u"Не удалось обработать список товаров")
    if showall:
        products = SoftServiceProduct.query.all()
    else:
        products = SoftServiceProduct.query.filter(SoftServiceProduct.cmpt_id == 0).all()
    return render_template("soft_helper/helper.html", products=products, showall=showall)


@app.route("/soft-<index>-<cmpt_id>", methods=["GET", "POST"])
@timer
def soft_sel(index, cmpt_id):
    product = SoftServiceProduct.query.get(int(index))
    if cmpt_id != '0':
        set_soft_id(int(index), int(cmpt_id))
        count = db.session.query(SoftServiceProduct).count()
        while True:
            product = SoftServiceProduct.query.get(product.id + 1)
            if product.cmpt_id == 0:
                return redirect("/soft-" + str(product.id) + "-0")
    filter_text = ""
    if request.method == "POST":
        print request.form
        filter_text = request.form["filter"].strip()

    res = search_product(product.name, filter_text)
    return render_template("soft_helper/search.html", product=product, res=res)
