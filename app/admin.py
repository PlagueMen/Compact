# -*- coding: utf-8 -*-
import os.path as op

from flask.ext import admin, login
from wtforms import fields, widgets
from flask.ext.admin import Admin
from flask.ext.admin.contrib import sqlamodel
from flask.ext.admin.base import MenuLink
from flask.ext.admin.contrib.fileadmin import FileAdmin

from app import app, db
from app.models import News, User, Partner


# Define wtforms widget and field
class CKTextAreaWidget(widgets.TextArea):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('class_', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(fields.TextAreaField):
    widget = CKTextAreaWidget()

# Customized admin interface
class PageAdmin(sqlamodel.ModelView):
    edit_template = create_template = 'admin/edit.html'

    def is_accessible(self):
        return login.current_user.is_authenticated()


class UserPageAdmin(PageAdmin):
    column_labels = dict(email='E-Mail', password='Пароль', first_name='Имя', second_name='Фамилия',
                         last_name='Отчество', phone='Телефон', discont='Номер ДК', role='Права')


class NewsPageAdmin(PageAdmin):
    form_overrides = dict(text=CKTextAreaField, description=CKTextAreaField)
    column_labels = dict(title='Заголовок', active='Активно', description='Краткий текст', text='Текст',
                         creation_date='Дата публикации')


class PartnersPageAdmin(PageAdmin):
    column_exclude_list = ['logo', 'description']
    form_overrides = dict(logo=CKTextAreaField, description=CKTextAreaField)
    column_labels = dict(title='Заголовок', active='Активно', logo='Логитип', name='Наименование',
                         description='Описание')


admin = Admin(app)

admin.add_view(UserPageAdmin(User, db.session, name="Пользователи"))
admin.add_view(NewsPageAdmin(News, db.session, name="Новости"))
admin.add_view(PartnersPageAdmin(Partner, db.session, name="Партнеры"))

path = op.join(op.dirname(__file__), 'static/upload')
admin.add_view(FileAdmin(path, '/upload/', name='Файлы'))

# Add home link by url
admin.add_link(MenuLink(name='Вернуться на сайт', url='/'))
