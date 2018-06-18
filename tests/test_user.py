import os
import unittest

from api import app

class CreateUserTestCase(unittest.TestCase):
    """
    Class represents api test case
    """
    def setUp(self):
        """
        store data before test runs
        """
        self.app = app.test_client
        self.user_1 = { "username":"userone", "name":"User One", "email":"user_1@maintenance_tracker.com", "password":"user1123", "confirm_password": "user1123"}


    def tearDown(self):
        """
        cleans data after test runs
        """
        self.user_1.clear()

    def test_sign_up_user(self):
        """
        test api can register a new user
        """
        results = self.client()

if __name__=='__main__':
    unittest.main()