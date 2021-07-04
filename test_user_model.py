"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test User class."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u1 = User.signup("testuser1", "test1@test.com", "HASHED_PASSWORD1", None)
        uid1 = 1
        u1.id = uid1
        u2 = User.signup("testuser2", "test2@test.com", "HASHED_PASSWORD", None)
        uid2 = 2
        u2.id = uid2

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def teardown(self):
        """Runs after every test"""

        res = super().teardown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        u.id = 4

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_repr(self):
        """Does the repr display what is expected?"""

        self.assertEqual(repr(self.u1), f"<User #1: testuser1, test1@test.com>")

    def test_user_is_following(self):
        """Does is_following detect if user1 is following user2 or not?"""

        self.u1.following.append(self.u2)
        db.session.commit()
        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u2))

    def test_user_is_followed_by(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?
        Does is_followed_by successfully detect when user1 is not followed by user2?"""

        self.u1.following.append(self.u2)
        db.session.commit()
        self.assertFalse(self.u1.is_followed_by(self.u2))
        self.assertTrue(self.u2.is_followed_by(self.u1))

    def test_user_signup(self):
        """Does User.create successfully create a new user given valid credentials?
        Does User.create fail to create a new user if any of the validations fail?"""

        new_user = User.signup("testuser3", "test3@test.com", "HASHED_PASSWORD", None)

        new_user.id = 3
        db.session.commit()
        new_user_test = User.query.get(new_user.id)
        self.assertTrue(new_user_test.username == "testuser3")
        self.assertTrue(new_user_test.email == "test3@test.com")
        # Is the password a brcypt hash string?
        self.assertTrue(new_user_test.password.index("$2b$") != -1)

    def test_user_authenticate(self):
        """Does User.authenticate successfully return a user when given a valid username and password?
        Does User.authenticate fail to return a user when the username is invalid?
        Does User.authenticate fail to return a user when the password is invalid?"""
        
        self.assertTrue(User.authenticate("testuser1", "HASHED_PASSWORD1"))
        self.assertFalse(User.authenticate("nottestuser1", "HASHED_PASSWORD1"))
        self.assertFalse(User.authenticate("testuser1", "wrong_password"))

