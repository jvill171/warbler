"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_messages_add(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            # GET ROUTE
            resp_g = c.get("/messages/new")
            self.assertEqual(resp_g.status_code, 200)

            # POST ROUTE
            resp_p = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp_p.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_messages_show(self):
        """Does /messages/<int:message_id> show a single message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            # Generate a message
            c.post("/messages/new", data={"text": "Hello"})
            # Retrieve message for testing
            msg = Message.query.one()

            resp = c.get(f"/messages/{msg.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<p class="single-message">{msg.text}', html)

    def test_messages_destroy(self):
        """Does /messages/<int:message_id>/delete delete a message"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            # Generate a message
            c.post("/messages/new", data={"text": "Hello"})
            # Retrieve message for testing
            msg = Message.query.one()

            resp = c.post(f"/messages/{msg.id}/delete")

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(Message.query.first(), None)

    def test_message_like(self):
        """Does /users/add_like/<int:message_id> toggle likes & redirect"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            # Generate a message
            c.post("/messages/new", data={"text": "Hello"})
            # Retrieve message for testing
            msg = Message.query.one()
            # Like the message
            resp = c.post(f"/users/add_like/{msg.id}")
            like = Likes.query.one()
            
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(msg.id, like.message_id)

            # Toggling to UN-like
            c.post(f"/users/add_like/{msg.id}")
            # Ensure the single like has been removed
            self.assertEqual(Likes.query.first(), None)

    def test_show_likes(self):
        """Does /users/<int:user_id>/likes show only liked posts?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            # Generate a few message
            c.post("/messages/new", data={"text": "Message 1"})
            c.post("/messages/new", data={"text": "Message 2"})
            c.post("/messages/new", data={"text": "Message 3"})
            c.post("/messages/new", data={"text": "Message 4"})

            all_messages = Message.query.all()
            msg_1 = all_messages[0]
            msg_2 = all_messages[1]
            msg_3 = all_messages[2]
            msg_4 = all_messages[3]

            # Like messages
            resp = c.post(f"/users/add_like/{msg_1.id}")
            resp = c.post(f"/users/add_like/{msg_2.id}")
            # DONT like msg_3
            resp = c.post(f"/users/add_like/{msg_4.id}")
            
            resp = c.get(f"/users/{self.testuser.id}/likes")
            like_msg_ids = {l.message_id for l in Likes.query.all()}
            
            self.assertEqual(resp.status_code, 200)
            
            # Check that all but msg_3 are liked
            self.assertIn(msg_1.id, like_msg_ids)
            self.assertIn(msg_2.id, like_msg_ids)
            self.assertNotIn(msg_3.id, like_msg_ids)
            self.assertIn(msg_4.id, like_msg_ids)

