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


class AssignedQuestion(Base):
    __tablename__ = "assigned_questions"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    question_id = Column(String)
    strategy = Column(String)

    def __init__(self, username, question_id, strategy):
        self.username = username
        self.question_id = question_id
        self.strategy = strategy


class InteractionLog(Base):
    __tablename__ = "interaction_log"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    question_id = Column(String)
    session_id = Column(String)
    interaction = Column(String)
    answer = Column(String)
    query = Column(String)
    time = Column(DateTime)
    data = Column(String)

    def __init__(self, username, question_id, session_id, interaction, answer, query, time, data=''):
        self.username = username
        self.question_id = question_id
        self.session_id = session_id
        self.answer = answer
        self.interaction = interaction
        self.query = query
        self.time = time
        self.data = data


if __name__ == '__main__':
    # create tables
    Base.metadata.create_all(engine)
