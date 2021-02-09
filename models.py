import os
from sqlalchemy import Column, String, create_engine, Integer
from flask_sqlalchemy import SQLAlchemy
import json, datetime

database_path = os.environ['DATABASE_URL']

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''

def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

    
#----------------------------------------------------------------------------#
# Models movies and actors TEST
#----------------------------------------------------------------------------#


class Movies(db.Model):  
  __tablename__ = 'Movies'

  id = Column(Integer, primary_key=True)
  title = Column(String, unique=True, nullable=False)
  release_date = Column (datetime, nullable=False)
 
  def __init__(self, title, release_date):
    self.title = title
    self.release_date = release_date
  
  def insert(self):
    db.session.add(self)
    db.session.commit()
  
    def update(self):
    db.session.commit()

    def delete(self):
    db.session.delete(self)
    db.session.commit()  

  def format(self):
    return {
      'id': self.id,
      'title': self.title,
      'release_date': self.release_date}

class Actors(db.Model):  
  __tablename__ = 'Actors'

  id = Column(Integer, primary_key=True)
  name = Column(String)
  age = Column(Integer)
  gender = Column(String)

  def __init__(self, title, release_date):
    self.name = name
    self.age = age
    self.gender = gender
  
  def insert(self):
    db.session.add(self)
    db.session.commit()
  
    def update(self):
    db.session.commit()

    def delete(self):
    db.session.delete(self)
    db.session.commit()  

  def format(self):
    return {
      'id': self.id,
      'name': self.name,
      'age': self.age,
      'gender': self.gender}
