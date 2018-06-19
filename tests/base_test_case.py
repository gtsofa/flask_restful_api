# tests/base_test_case.py
from datetime import datetime, timedelta

import jwt

from flask_testing import TestCase

from app.v2.models import Users, Todo
from config import Config
from manage import app, db
from config import app_config

app.config.from_object(app.config["testing"])

class BaseTestCase(TestCase):
    """
    Base configurations for the tests
    """
    def create_app(self):
        """
        return app
        """
        #app.config.from_object(config_environments['testing'])
        return app

    def setUp(self):
        """
        create test data and set up test client
        """
        self.client = self.app.testing_client()
        db.create_all()
        
        # add a test user to the db
        user = Users("TestUser", "testpassword")
        todo1 = Todo(complete=False, text="Create a Youtube video", created_by=1)
        todo2 = Todo(complete=False, text="I want to go shopping", created_by=1)

        db.session.add(user)
        db.session.add(todo1)
        db.session.add(todo2)
        db.session.commit()

        # generate token

    def tearDown(self):
        """
        Destroy test data
        """
        db.session.remove()
        db.drop_all()

if __name__ =='__main__':
    nose.run()
