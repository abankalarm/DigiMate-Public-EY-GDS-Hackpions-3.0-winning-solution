# -*- encoding: utf-8 -*-

from sqlalchemy.sql.elements import Null
from sqlalchemy.sql.sqltypes import Date
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String , JSON
#from sqlalchemy import Binary
from app import db, login_manager
import json
#from sqlalchemy import Binary

from app.base.util import hash_pass

class User(db.Model, UserMixin):

    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    #password = Column(Binary)
    password = Column(String)

    # all faltu bakwas
    dob = Column(String)
    department = Column(String)
    # skills1 = Column(String)
    # skills2 = Column(String)
    # skills3 = Column(String)
    # skills4 = Column(String)
    # skills5 = Column(String)
    skills= Column(String)
    Gender = Column(String)
    MaritalStatus = Column(String)
    PercentSalaryHike = Column(String)
    StockOptionLevel    = Column(String)
    extra = Column(String)
    YearsAtCompany  = Column(String)
    YearsInCurrentRole = Column(String)
    education = Column(String)
    recruitment_type = Column(String)
    job_level = Column(String)
    rating = Column(String)
    onsite = Column(String)
    salary = Column(String)
    height = Column(String)
    weight = Column(String)
    SkillPointEarned=Column(String)
    tasks = Column(String)
    def __init__(self, **kwargs):
        skills=[]
        templist=['skills1','skills2','skills3','skills4','skills5']
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            print(property)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            elif property == 'password':
                value = hash_pass( value ) # we need bytes here (not plain str)
                
            elif property in templist:
                skills.append(value)
                continue
                


            setattr(self, property, value)
        print(skills)
        setattr(self, "skills", json.dumps({"skills":skills}))

    def __repr__(self):
        return "<User(name='%s', fullname='%s', nickname='%s')>" % (
                                self.username, self.email, self.password)


@login_manager.user_loader
def user_loader(id):
    return User.query.filter_by(id=id).first()

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    return user if user else None
