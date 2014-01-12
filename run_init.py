# -*- coding: utf-8 -*-
from app.models import User
from app import db

user = User()
user.email = 'plaguemen@gmail.com'
user.first_name = u'Грачёв'
user.second_name = u'Александр'
user.last_name = u'Сергеевич'
user.password = u'111'
user.phone_number = '9517675299'
user.role = 2
db.create_all()
try:
    db.session.add(user)
    db.session.commit()
except:
    pass
