from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from flask_login import UserMixin
import os, json, pickle as pk
import numpy as np
from common.parser.lc_quad_linked import LC_Qaud_Linked
import argparse

Base = declarative_base()


class User(Base, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)

    def __init__(self, username, email, password):
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
    question_id = Column(String)
    strategy = Column(String)

    def __init__(self, username, question_id, strategy):
        self.username = username
        self.question_id = question_id
        self.strategy = strategy


class AnsweredQuestion(Base):
    __tablename__ = "answered_questions"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    question_id = Column(String)
    strategy = Column(String)
    time = Column(DateTime)
    duration = Column(Integer)
    data = Column(String)
    final_query = Column(String)

    def __init__(self, username, question_id, strategy, time, duration, data, final_query):
        self.username = username
        self.question_id = question_id
        self.strategy = strategy
        self.time = time
        self.duration = duration
        self.data = data
        self.final_query = final_query


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


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    complexity = Column(Integer)
    text = Column(String)

    def __init__(self, id, complexity, text):
        self.id = id
        self.complexity = complexity
        self.text


class AssignedTask(Base):
    __tablename__ = "assigned_tasks"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    question_id = Column(String)
    strategy = Column(String)

    def __init__(self, username, question_id, strategy):
        self.username = username
        self.question_id = question_id
        self.strategy = strategy


class AnsweredTask(Base):
    __tablename__ = "answered_tasks"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    question_id = Column(String)
    strategy = Column(String)
    time = Column(DateTime)
    duration = Column(Integer)
    data = Column(String)
    final_query = Column(String)

    def __init__(self, username, question_id, strategy, time, duration, data, final_query):
        self.username = username
        self.question_id = question_id
        self.strategy = strategy
        self.time = time
        self.duration = duration
        self.data = data
        self.final_query = final_query


class TaskInteractionLog(Base):
    __tablename__ = "task_interaction_log"

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
    parser = argparse.ArgumentParser(description='Create tables for IQA')
    parser.add_argument("--base_path", help="base path", default="../../", dest="base_path")
    parser.add_argument("--def_users", dest='def_users', action='store_true')
    args = parser.parse_args()

    engine = create_engine('sqlite:///{0}'.format(os.path.join(args.base_path, 'UI', 'database', 'IQA.db')))

    create_tables = True
    if create_tables:
        Base.metadata.create_all(engine)

    if args.def_users:
        users = [
            "1,'Jens','jens.lehmann@cs.uni-bonn.de','sha256$fo4Uw234$d28c32c3f9c1e4da53dfa22a62373759174252d1aba2ec1ca6e681ced2ccd291'",
            "2,'hamid','hamid.zafar.tud@gmail.com','sha256$FrQhkuX9$6d0bcefc3a9f77e5272e8fe70c050cc8ade02b1806d0971b00b4b86ff3306e23'",
            "3,'Dubey','mohnish.rygbee@gmail.com','sha256$mfbgluwf$4fe4f23a3c34a96e53a72902619656390c93adf874094fec77689c520de2cdea'",
            "4,'elena','demidova@l3s.de','sha256$vfap2HPS$f81d4bcd74ea4d53078416ca099e64f1ae70536a1db0fffe12e80ac173431500'"]
        for user in users:
            engine.execute('INSERT INTO users VALUES({0})'.format(user))

    dataset = LC_Qaud_Linked(os.path.join(args.base_path, 'data', 'LC-QuAD', 'linked.json'))
    question_complexities = {
        qapair.id: len([uri for uri in qapair.sparql.uris if not (uri.is_generic() or uri.is_type())]) for qapair in
        dataset.qapairs}

    populate_questions_table = False
    if populate_questions_table:
        with open(os.path.join(args.base_path, 'output', 'wdaqua_core1.pk'), "r") as data_file:
            wdaqua_results = pk.load(data_file)
        with open(os.path.join(args.base_path, 'output', 'stats-IQA-SO-RQ.json'), "r") as data_file:
            iqa_results = json.load(data_file)

        question_ids = os.listdir(os.path.join(args.base_path, 'output', 'pipeline'))
        for file_name in question_ids:
            question_id = file_name[:-7]
            if question_id in wdaqua_results and ((question_id + '+correct') in iqa_results):
                engine.execute(
                    'INSERT INTO questions VALUES("{0}",{1})'.format(question_id, question_complexities[question_id]))
        questions = list(engine.execute('SELECT * FROM questions'))
        print('#questions: {}'.format(len(questions)))
        print(
            'Dist. per complexity : {}'.format(np.unique([question[1] for question in questions], return_counts=True)))

    populate_assigned_question_table = False
    if populate_assigned_question_table:
        strategies = ['IO', 'OG']
        result = engine.execute('SELECT * FROM questions ORDER BY 2')
        number_of_users = 15
        number_of_question_per_complexity = {2: 10, 3: 10, 4: 9, 5: 1}
        question_complexities = {item[0]: item[1] for item in result}
        complexities = set(question_complexities.values())

        for user_idx in range(number_of_users):
            qids = []
            for c in complexities:
                for idx in range(number_of_question_per_complexity[c]):
                    candidate_qids = [item[0] for item in question_complexities.iteritems() if item[1] == c]
                    if len(candidate_qids) > 0:
                        qids.append(candidate_qids[0])
                        del question_complexities[candidate_qids[0]]
            for strategy in strategies:
                for qid in qids:
                    engine.execute(
                        'INSERT INTO assigned_questions(username, question_id) VALUES("#{0}-{1}","{2}")'.format(
                            str(user_idx), strategy, qid))

    populate_tasks_table = True
    if populate_tasks_table:
        with open(os.path.join(args.base_path, 'output', 'random_50.json'), "r") as data_file:
            tasks = json.load(data_file)
        for task in tasks:
            question_id = task[0]
            engine.execute(
                'INSERT INTO tasks VALUES("{0}",{1}, "{2}")'.format(question_id,
                                                                    question_complexities[question_id],
                                                                    task[1]))
        tasks = list(engine.execute('SELECT * FROM tasks'))
        print('#tasks: {}'.format(len(tasks)))
        print(
            'Dist. per complexity : {}'.format(np.unique([task[1] for task in tasks], return_counts=True)))

    populate_assigned_task_table = True
    if populate_assigned_task_table:
        strategies = ['IO']
        result = engine.execute('SELECT * FROM tasks ORDER BY 2')
        number_of_users = 10
        number_of_question_per_complexity = {2: 2, 3: 2, 4: 1, 5: 1}
        question_complexities = {item[0]: item[1] for item in result}
        complexities = set(question_complexities.values())

        for user_idx in range(number_of_users):
            qids = []
            for c in complexities:
                for idx in range(number_of_question_per_complexity[c]):
                    candidate_qids = [item[0] for item in question_complexities.items() if item[1] == c]
                    if len(candidate_qids) > 0:
                        qids.append(candidate_qids[0])
                        del question_complexities[candidate_qids[0]]
            for strategy in strategies:
                for qid in qids:
                    engine.execute(
                        'INSERT INTO assigned_tasks(username, question_id) VALUES("#{0}-{1}","{2}")'.format(
                            str(user_idx), strategy, qid))