import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgresql://{}:{}@{}/{}".format("postgres1", "postgres1", "localhost:5433", self.database_name)
        setup_db(self.app, self.database_path)

       
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    def test_search(self):
        search = {'searchTerm': 'discov', }
        res = self.client().post('/search', json=search)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 10)

    def test_delete(self):
        res = self.client().delete('/questions/1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_add_question(self):
        question = {
            'question': 'Testing New Question?',
            'answer': 'Testing is ok',
            'difficulty': 3,
            'category': 2
        }
        res = self.client().post('/questions', json=question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
    
    def test_quiz(self):
        quiz = {
            'previous_questions': [10],
            'quiz_category': {
                'type': 'science',
                'id': '1'
            }
        }
        res = self.client().post('/quizzes', json=quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question']['category'], '1')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()