from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.babelex import Babel
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.contrib.cache import MemcachedCache
#from flask.ext.cache import Cache

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config.from_object('config')
db = SQLAlchemy(app)
lm = LoginManager(app)
lm.login_view = 'login'
cache = MemcachedCache()
babel = Babel(app)

from app import views, models, admin
