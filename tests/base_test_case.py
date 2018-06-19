# tests/base_test_case.py
from datetime import datetime, timedelta

import jwt

from flask_testing import TestCase

from app.v2.models import Users, Todo
from config import Config, config_environments
from manage import app, db

class BaseTestCase(TestCase):
    """
    Base configurations for the tests
    """
    def create_app(self):
        app.config.from_object(config_environments['testing'])
        return app

    def setUp(self):
        self.client = self.app.testing_client()
        db.drop_all()
        db.create_all()

        # add a test user to the db
        user = Users("TestUser", "password")
        db.session.add()
        db.session.commit()

        # generate token
        