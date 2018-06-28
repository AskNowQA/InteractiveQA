from random import randint
from sqlalchemy import create_engine


class BookKeeper:
    def __init__(self, db_path):
        self.engine = create_engine('sqlite:///' + db_path)

    def new_question(self, userid, qid=None):
        # for debugging purposes
        if qid is not None:
            return qid

        result = list(self.engine.execute('SELECT * FROM assigned_questions WHERE username = "{}"'.format(userid)))
        if len(result) > 0:
            questions = [item[2] for item in result]

            answered_questions = list(
                self.engine.execute('SELECT * FROM answered_questions WHERE username = "{}"'.format(userid)))
            for row in answered_questions:
                qid = row[2]
                if qid in questions:
                    questions.remove(qid)
            return questions[randint(0, len(questions) - 1)]
        else:
            result = list(
                self.engine.execute('SELECT min(username) FROM assigned_questions WHERE substr(username,1,1)="#"'))
            if len(result) > 0:
                result = result[0]
                self.engine.execute(
                    'UPDATE assigned_questions SET username = "{0}" WHERE username = "{1}"'.format(userid, result[0]))
            return self.new_question(userid)
