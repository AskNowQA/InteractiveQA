from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from flask_login import UserMixin
import os, json, pickle as pk
from common.parser.lc_quad_linked import LC_Qaud_Linked

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


class Question(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True)
    complexity = Column(Integer)

    def __init__(self, id, complexity):
        self.id = id
        self.complexity = complexity


class AssignedQuestion(Base):
    __tablename__ = "assigned_questions"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    question_ids = Column(String)

    def __init__(self, username, question_ids):
        self.username = username
        self.question_ids = question_ids


class AnsweredQuestion(Base):
    __tablename__ = "answered_questions"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    question_id = Column(String)
    strategy = Column(String)
    time = Column(DateTime)
    duration = Column(Integer)

    def __init__(self, username, question_id, strategy, time, duration):
        self.username = username
        self.question_id = question_id
        self.strategy = strategy
        self.time = time
        self.duration = duration


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
    create_tables = False
    if create_tables:
        Base.metadata.create_all(engine)

    populate_questions_table = False
    base_path = "../../"
    if populate_questions_table:
        dataset = LC_Qaud_Linked(os.path.join(base_path, 'data', 'LC-QuAD', 'linked.json'))
        question_complexities = {
            qapair.id: len([uri for uri in qapair.sparql.uris if not (uri.is_generic() or uri.is_type())]) for qapair in
            dataset.qapairs}

        with open(os.path.join(base_path, 'output', 'wdaqua_core1.pk'), "r") as data_file:
            wdaqua_results = pk.load(data_file)

        question_ids = os.listdir(os.path.join(base_path, 'output', 'pipeline'))
        for file_name in question_ids:
            question_id = file_name[:-7]
            if question_id in wdaqua_results:
                engine.execute(
                    'INSERT INTO questions VALUES("{0}",{1})'.format(question_id, question_complexities[question_id]))

    populate_assigned_question_table = False
    if populate_assigned_question_table:
        result = engine.execute('SELECT * FROM questions ORDER BY 2')
        number_of_users = 5
        number_of_question_per_complexity = 2
        question_complexities = {item[0]: item[1] for item in result}
        complexities = set(question_complexities.values())

        for user_idx in range(number_of_users):
            qids = []
            for c in complexities:
                for idx in range(number_of_question_per_complexity):
                    candidate_qids = [item[0] for item in question_complexities.iteritems() if item[1] == c]
                    if len(candidate_qids) > 0:
                        qids.append(candidate_qids[0])
                        del question_complexities[candidate_qids[0]]
            engine.execute(
                'INSERT INTO assigned_questions(question_ids) VALUES("{0}")'.format('-'.join(qids)))

    result = engine.execute('SELECT * FROM assigned_questions')
    print(list(result))
