"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows
from datetime import datetime

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

USER_DATA_1 = { "email": "one@test.com",
            "username": "testuser1",
            "password": "HASHED_PASSWORD_1"}
MSG_1 = Message(text="TEST MESSAGE 1")
MSG_2 = Message(text="TEST MESSAGE 2")
MSG_3 = Message(text="TEST MESSAGE 3")
MSG_4 = Message(text="TEST MESSAGE 4")
# Generate timestamp for equality validation
MSG_TIMESTAMP = datetime.utcnow()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()
        
    # def tearDown(self):
    #     '''Clean up any transactions'''
    #     db.session.rollback()

    def test_user_message(self):
        """Does basic model work?"""

        u = User(**USER_DATA_1)
        db.session.add(u)
        db.session.commit()

        m = Message(
            text = "Test Message 1" ,
            timestamp = MSG_TIMESTAMP,
            user_id = u.id
            )
        db.session.add(m)
        db.session.commit()
        
        self.assertEqual(m.user, u)
        self.assertEqual(len(u.messages), 1)

    def test_add_message(self):
        """Does adding to a users's messages work"""
        
        u = User(**USER_DATA_1)
        db.session.add(u)
        db.session.commit()

        m = MSG_1
        # Check the message is NOT in u.messages
        self.assertNotIn(m, u.messages)

        u.messages.append(m)
        db.session.commit()
        # Check the message IS in u.messages
        self.assertIn(m, u.messages)
    
    def test_add_multiple_messags(self):
        """Does Message register multiple messages"""
        
        u = User(**USER_DATA_1)
        db.session.add(u)
        db.session.commit()

        m1 = MSG_1
        m2 = MSG_2
        m3 = MSG_3
        m4 = MSG_4

        # Check the message are NOT in u.messages
        self.assertEqual(len(u.messages), 0)
        self.assertNotIn(m1, u.messages)
        self.assertNotIn(m2, u.messages)
        self.assertNotIn(m3, u.messages)
        self.assertNotIn(m4, u.messages)

        u.messages.append(m1)
        u.messages.append(m2)
        u.messages.append(m3)
        u.messages.append(m4)
        db.session.commit()

        # Check the messages ARE in u.messages
        self.assertEqual(len(u.messages), 4)
        self.assertIn(m1, u.messages)
        self.assertIn(m2, u.messages)
        self.assertIn(m3, u.messages)
        self.assertIn(m4, u.messages)
    
    def test_delete_message(self):
        """Does a message get deleted properly"""
        
        u = User(**USER_DATA_1)
        db.session.add(u)
        db.session.commit()

        m1 = MSG_1
        m2 = MSG_2
        m3 = MSG_3
        m4 = MSG_4

        self.assertEqual(len(u.messages), 0)

        u.messages.append(m1)
        u.messages.append(m2)
        u.messages.append(m3)
        u.messages.append(m4)
        db.session.commit()

        self.assertEqual(len(u.messages), 4)

        # Delete message 1
        db.session.delete(m1)
        db.session.commit()

        self.assertNotIn(m1, u.messages)
        self.assertEqual(len(u.messages), 3)
        
        # Delete messages 3 & 4
        db.session.delete(m3)
        db.session.delete(m4)
        db.session.commit()
        
        self.assertNotIn(m3, u.messages)
        self.assertNotIn(m4, u.messages)
        self.assertEqual(len(u.messages), 1)
        
        # Check the last message is still there
        self.assertIn(m2, u.messages)
