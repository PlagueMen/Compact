import os

basedir = os.path.abspath(os.path.dirname(__file__))
APP_DIR = os.path.join(basedir, "app")

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
DEBUG = False
CACHE_TYPE = 'memcached'

SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://cmpt_mysql:mylighting@/cmpt_shop?charset=utf8&use_unicode=0"
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, '../cmpt_shop/db_repository')

BABEL_DEFAULT_LOCALE = "ru"

USER_IMG_DIR = os.path.join(APP_DIR, 'static/upload/img')
