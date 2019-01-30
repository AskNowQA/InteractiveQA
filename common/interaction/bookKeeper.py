from random import randint
from sqlalchemy import create_engine


class BookKeeper:
    def __init__(self, db_path):
        self.engine = create_engine('sqlite:///' + db_path)

    def new_question(self, userid, qid=None):
        # for debugging purposes
        if qid is not None:
            return qid, 1, 1

        result = list(self.engine.execute('SELECT * FROM assigned_questions WHERE username = "{}"'.format(userid)))
        total_question = len(result)
        if len(result) > 0:
            questions = [item[2] for item in result]

            answered_questions = list(
                self.engine.execute('SELECT * FROM answered_questions WHERE username = "{}"'.format(userid)))
            for row in answered_questions:
                qid = row[2]
                if qid in questions:
                    questions.remove(qid)
            if len(questions) == 0:
                return None, 0, 0
            return questions[randint(0, len(questions) - 1)], total_question, len(answered_questions)
        else:
            result = list(
                self.engine.execute('SELECT min(username) FROM assigned_questions WHERE substr(username,1,1)="#"'))
            if len(result) > 0:
                result = result[0]
                self.engine.execute(
                    'UPDATE assigned_questions SET username = "{0}" WHERE username = "{1}"'.format(userid, result[0]))
            return self.new_question(userid)

    def new_task(self, userid):
        result = list(self.engine.execute('SELECT * FROM assigned_tasks WHERE username = "{}"'.format(userid)))
        total_task = len(result)
        if len(result) > 0:
            tasks = [item[2] for item in result]

            answered_tasks = list(
                self.engine.execute('SELECT * FROM answered_tasks WHERE username = "{}"'.format(userid)))
            for row in answered_tasks:
                qid = row[2]
                if qid in tasks:
                    tasks.remove(qid)
            if len(tasks) == 0:
                return None, 0, 0
            qid = tasks[randint(0, len(tasks) - 1)]
            selected_task = list(
                self.engine.execute('SELECT * FROM tasks WHERE id = "{}"'.format(qid)))[0][2]
            return qid, selected_task, total_task, len(answered_tasks)
        else:
            result = list(
                self.engine.execute('SELECT min(username) FROM assigned_tasks WHERE substr(username,1,1)="#"'))
            if len(result) > 0:
                result = result[0]
                self.engine.execute(
                    'UPDATE assigned_tasks SET username = "{0}" WHERE username = "{1}"'.format(userid, result[0]))
            return self.new_task(userid)
