import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category, db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
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

    def test_paginate_questions(self):
        # Tests question pagination success
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self-assertEqual(data['success'], True)

    def test_404_request_beyond_valid_page(self):
        response = self.client().get('/questions?page=1000', json['rating': 1])
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_categories(self):

    def test_get_questions(self):

    def test_delete_question(self):
        """ Tests question delete success """
        #create a new question to be deleted
        test_question = Question(question="is a test?", answer='yes', category=1, difficulty=1)
        test_question.insert()
        q_id = test_question.id

        questions_before = Question.query.all()

        response = self.client.delete('/questions/{}'.format(q_id))
        data = json.loads(response.data)

        questions_after = Question.query.all()
        test_question = Question.query.filter(Question.id == 1).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        self.asserEqual(data['deleted'], q_id)

        self.assertTrue(len(questions_before) - len(questions_after == 1))

        self.assertEqual(test_question, None)
        

    def test_create_question(self):

    def test_search_question(self):

    def test_get_category_questions(self):

    def test_get_quiz(self):


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()