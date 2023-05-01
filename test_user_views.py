"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

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


class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()
        
        # This will be the logged in user
        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser1 = User.signup(username="testuser1",
                                    email="test1@test.com",
                                    password="testuser1",
                                    image_url=None)

        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)
        

        db.session.commit()
##############################################################################
# Test routes as a guest (not logged in)
    def test_list_users_guest(self):
        """Is a list of all users shown? (guest)"""

        with self.client as c:

            resp = c.get("/users")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            # Check that all (2) test users are shown in the HTML
            self.assertIn("<p>@testuser</p>", html)
            self.assertIn("<p>@testuser1</p>", html)
            self.assertIn("<p>@testuser2</p>", html)
            
    def test_users_show_guest(self):
        """Is a the specified user's profile shown? (guest) """

        with self.client as c:

            # Create a message for testuser1
            self.testuser1.messages.append(
                Message(text="I am the first message from testuser1")
            )
            # Ensure only messages from testuser1 show up, by creating a message for testuser2
            self.testuser2.messages.append(
                Message(text="I am the first message from testuser2")
            )
            db.session.commit()

            resp = c.get(f"/users/{self.testuser1.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            
            # Ensure only messages form this user's profile show up 
            self.assertIn("<p>I am the first message from testuser1</p>", html)
            self.assertNotIn("<p>I am the first message from testuser2</p>", html)
            
            # Ensure the profile is being viewed as a guest
            self.assertNotIn('class="btn btn-outline-secondary">Edit Profile', html)
            self.assertNotIn('<button class="btn btn-primary">Unfollow', html)
            self.assertNotIn('<button class="btn btn-outline-primary">Follow', html)
    
    def test_show_following_guest(self):
        """Is access denied to view who a user is following? (guest)"""

        with self.client as c:
            resp = c.get(f"/users/{self.testuser1.id}/following")
            # Check user is redirected
            self.assertEqual(resp.status_code, 302)

            # Follow redirects to check that flash message is "Unauthorized"
            resp = c.get(f"/users/{self.testuser1.id}/following", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', html)
            self.assertIn('<li><a href="/signup">Sign up</a></li>', html)
            self.assertIn('<li><a href="/login">Log in</a></li>', html)
    
    def test_users_followers_guest(self):
        """Is access denied to view a user's followers (guest)"""

        with self.client as c:
            resp = c.get(f"/users/{self.testuser1.id}/followers")
            # Check user is redirected
            self.assertEqual(resp.status_code, 302)

            # Follow redirects to check that flash message is "Unauthorized"
            resp = c.get(f"/users/{self.testuser1.id}/followers", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', html)
            self.assertIn('<li><a href="/signup">Sign up</a></li>', html)
            self.assertIn('<li><a href="/login">Log in</a></li>', html)
        
    def test_add_follow_guest(self):
        """Is access denied to add a follow (guest)"""

        with self.client as c:
            resp = c.post(f"/users/follow/{self.testuser1.id}")
            # Check user is redirected
            self.assertEqual(resp.status_code, 302)

            # Follow redirects to check that flash message is "Unauthorized"
            resp = c.post(f"/users/follow/{self.testuser1.id}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', html)
            self.assertIn('<li><a href="/signup">Sign up</a></li>', html)
            self.assertIn('<li><a href="/login">Log in</a></li>', html)

    def test_stop_following_guest(self):
        """Is access denied to stop a follow (guest)"""

        with self.client as c:
            resp = c.post(f"/users/stop-following/{self.testuser1.id}")
            # Check user is redirected
            self.assertEqual(resp.status_code, 302)

            # Follow redirects to check that flash message is "Unauthorized"
            resp = c.post(f"/users/stop-following/{self.testuser1.id}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', html)
            self.assertIn('<li><a href="/signup">Sign up</a></li>', html)
            self.assertIn('<li><a href="/login">Log in</a></li>', html)
        
    def test_profile_guest(self):
        """Is access denied to update a user's profile (guest)"""

        with self.client as c:
            resp = c.post("/users/profile")
            # Check user is redirected
            self.assertEqual(resp.status_code, 302)

            # Follow redirects to check that flash message is "Unauthorized"
            resp = c.post("/users/profile", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', html)
            self.assertIn('<li><a href="/signup">Sign up</a></li>', html)
            self.assertIn('<li><a href="/login">Log in</a></li>', html)
        
    def test_delete_user_guest(self):
        """Is access denied to delete a user (guest)"""

        with self.client as c:
            resp = c.post("/users/delete")
            # Check user is redirected
            self.assertEqual(resp.status_code, 302)

            # Follow redirects to check that flash message is "Unauthorized"
            resp = c.post("/users/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', html)
            self.assertIn('<li><a href="/signup">Sign up</a></li>', html)
            self.assertIn('<li><a href="/login">Log in</a></li>', html)
        