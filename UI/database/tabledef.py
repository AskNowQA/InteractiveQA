from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from flask_login import UserMixin

engine = create_engine('sqlite:///IQA.db', echo=True)
Base = declarative_base()


class User(Base, UserMixin):
    """"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)

    # ----------------------------------------------------------------------
    def __init__(self, username, email, password):
        """"""
        self.username = username
        self.email = email
        self.password = password


# create tables
Base.metadata.create_all(engine)
