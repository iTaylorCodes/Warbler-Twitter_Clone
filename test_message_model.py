import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app


db.create_all()

class MessageModelTestCase(TestCase):
    """Test Message class."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.u1 = User.signup("testuser1", "test1@test.com", "HASHED_PASSWORD1", None)
        self.uid1 = 5
        self.u1.id = self.uid1
        self.u2 = User.signup("testuser2", "test2@test.com", "HASHED_PASSWORD", None)
        self.uid2 = 6
        self.u2.id = self.uid2
        db.session.commit()

        self.client = app.test_client()

    def teardown(self):
        """Runs after every test"""

        res = super().teardown()
        db.session.rollback()
        return res

    def test_message_model(self):
        """Does basic model work?"""

        m = Message(
            text="test message",
            user_id=self.uid2
        )

        db.session.add(m)
        db.session.commit()

        self.assertEqual(len(self.u2.messages), 1)
        self.assertEqual(self.u2.messages[0].text, "test message")

    def test_message_likes(self):
        "Can a user like another user's post?"

        m1 = Message(text="test message 1", user_id=self.uid1)

        m2 = Message(text="test message 2", user_id=self.uid1)

        db.session.add_all(
            [
                m1,
                m2,
            ]
        )
        db.session.commit()

        self.u2.likes.append(m1)

        db.session.commit()

        user2_likes = Likes.query.filter(Likes.user_id == self.uid2).all()
        self.assertEqual(len(user2_likes), 1)