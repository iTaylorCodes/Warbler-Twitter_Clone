import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows

os.environ["DATABASE_URL"] = "postgresql:///warbler_test"

from app import app, CURR_USER_KEY

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config["WTF_CSRF_ENABLED"] = False


class UserViewTestCase(TestCase):
    """Test views for user."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()
        self.u1 = User.signup("testuser1", "test1@test.com", "HASHED_PASSWORD1", None)
        self.uid1 = 10
        self.u1.id = self.uid1
        self.u2 = User.signup("testuser2", "test2@test.com", "HASHED_PASSWORD", None)
        self.uid2 = 11
        self.u2.id = self.uid2
        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_users_index(self):
        with self.client as c:
            resp = c.get("/users")

            self.assertIn("@testuser1", str(resp.data))
            self.assertIn("testuser2", str(resp.data))

    def test_users_search(self):
        with self.client as c:
            resp = c.get("/users?q=test")

            self.assertIn("@testuser1", str(resp.data))
            self.assertIn("@testuser2", str(resp.data))

    def test_user_show(self):
        """Does user page show up?"""
        with self.client as c:
            resp = c.get(f"/users/{self.uid1}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@testuser1", str(resp.data))

    def test_show_following(self):
        """Can a non logged in user see following page?
        Does it work if logged in?"""
        self.u1.following.append(self.u2)
        db.session.commit()

        resp = self.client.get(f"/users/{self.uid1}/following", follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Access unauthorized", html)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid1

            resp = c.get(f"/users/{self.uid1}/following", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)

            self.assertIn("@testuser2", html)

    def test_remove_followers(self):
        """Can a logged in user add and remove followers?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid1

            resp = c.post("/users/follow/11", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertIn("@testuser2", html)

            resp = c.post("/users/stop-following/11", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertNotIn("@testuser2", html)