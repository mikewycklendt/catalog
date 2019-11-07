import datetime
from sqlalchemy import Column,Integer,String, DateTime,Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context

Base = declarative_base()

Base = declarative_base()

class Category(Base):
	__tablename__ = 'category'
	id = Column(Integer, primary_key=True)
	name = Column(String)
	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
		'id': self.id,
		'name': self.name
		}

class Item(Base):
	__tablename__ = 'item'
	id = Column(Integer, primary_key=True)
	title = Column(String)
	cat_id = Column(Integer, ForeignKey('category.id'))
	description = Column(Text())
	user_id = Column(Integer, ForeignKey('user.id'))
	date_added = Column(DateTime, default=datetime.datetime.utcnow)
	category = relationship(Category, backref='item')
	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
		'id': self.id,
		'title': self.title,
		'cat_id': self.cat_id,
		'user_id': self.user_id,
		'description': self.description,
		'date_added': self.date_added
		}



class User(Base):
  __tablename__ = 'user'

  id = Column(Integer, primary_key=True)
  name = Column(String(250), nullable=False)
  email = Column(String(250), nullable=False)
  picture = Column(String(250))
  @property
  def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
		'id': self.id,
		'name': self.name,
		'email': self.email,
		'picture': self.picture,
		}

engine = create_engine('sqlite:///catalogApp.db')

Base.metadata.create_all(engine)