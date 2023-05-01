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
        
    
    def test_list_users(self):
        """
        Is a list of all users shown
        functions the same if logged in or not
        """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # No search parameters
            resp_e = c.get("/users")
            html = resp_e.get_data(as_text=True)

            self.assertEqual(resp_e.status_code, 200)
            # Check that all (2) test users are shown in the HTML
            self.assertIn("<p>@testuser</p>", html)
            self.assertIn("<p>@testuser1</p>", html)
            self.assertIn("<p>@testuser2</p>", html)
            
            resp_s = c.get("/users?q=1")
            html = resp_s.get_data(as_text=True)

            self.assertEqual(resp_s.status_code, 200)
            # Check that all (2) test users are shown in the HTML
            self.assertNotIn("<p>@testuser</p>", html)
            self.assertIn("<p>@testuser1</p>", html)
            self.assertNotIn("<p>@testuser2</p>", html)

##############################################################################
# Test routes as a guest (not logged in), most routes deny user access

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
        
##############################################################################
# Test routes as a logged in user
            
    def test_users_show_logged_in_other_profile(self):
        """.
        Is a the specified user's profile shown? (logged in)
        [NOT SELF PROFILE]
        """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            # Create a message for testuser
            self.testuser.messages.append(
                Message(text="I am logged in and messaging!")
            )

            # Create a message for testuser1
            self.testuser1.messages.append(
                Message(text="I am the first message from testuser1")
            )
            # Ensure only messages from testuser1 show up, by creating a message for testuser2
            self.testuser2.messages.append(
                Message(text="I am the first message from testuser2")
            )
            db.session.commit()

            # View someone else's profile
            resp = c.get(f"/users/{self.testuser1.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            
            # Ensure only messages form this user's profile show up 
            self.assertIn("<p>I am the first message from testuser1</p>", html)
            self.assertNotIn("<p>I am logged in and messaging!</p>", html)
            self.assertNotIn("<p>I am the first message from testuser2</p>", html)
            
            # Ensure the profile is being viewed as a guest
            self.assertNotIn('class="btn btn-outline-secondary">Edit Profile', html)
            self.assertNotIn('<button class="btn btn-primary">Unfollow', html)
            self.assertIn('<button class="btn btn-outline-primary">Follow', html)

    def test_users_show_logged_in_self_profile(self):
        """.
        Is a the specified user's profile shown? (logged in)
        [NOT SELF PROFILE]
        """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            # Create a message for testuser
            self.testuser.messages.append(
                Message(text="I am logged in and messaging!")
            )

            # Create a message for testuser1
            self.testuser1.messages.append(
                Message(text="I am the first message from testuser1")
            )
            # Ensure only messages from testuser1 show up, by creating a message for testuser2
            self.testuser2.messages.append(
                Message(text="I am the first message from testuser2")
            )
            db.session.commit()

            # View logged in user's profile
            resp = c.get(f"/users/{self.testuser.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            
            # Ensure only messages form this user's profile show up 
            self.assertIn("<p>I am logged in and messaging!</p>", html)
            self.assertNotIn("<p>I am the first message from testuser1</p>", html)
            self.assertNotIn("<p>I am the first message from testuser2</p>", html)
            
            # Ensure the profile is being viewed as a logged in user
            self.assertIn('class="btn btn-outline-secondary">Edit Profile', html)
            self.assertNotIn('<button class="btn btn-primary">Unfollow', html)
            self.assertNotIn('<button class="btn btn-outline-primary">Follow', html)
    
    def test_show_following_logged_in_other_profile(self):
        """Is users the another in user is following shown? (logged in)"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Follow testuser1, but not testuser2
            self.testuser1.following.append(self.testuser2)
            db.session.commit()
            
            resp = c.get(f"/users/{self.testuser1.id}/following")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            self.assertNotIn('class="btn btn-outline-secondary">Edit Profile', html)

            self.assertIn("<p>@testuser2</p>", html)
            self.assertNotIn("<p>@testuser</p>", html)

            self.assertIn('<button class="btn btn-outline-primary btn-sm">Follow</button>', html)
            self.assertNotIn('<button class="btn btn-primary btn-sm">Unfollow</button>', html)

    def test_show_following_logged_in_self(self):
        """Is users the logged in user is following shown? (logged in)"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Follow testuser1, but not testuser2
            self.testuser.following.append(self.testuser1)
            db.session.commit()
            
            resp = c.get(f"/users/{self.testuser.id}/following")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn('class="btn btn-outline-secondary">Edit Profile', html)

            self.assertIn("<p>@testuser1</p>", html)
            self.assertNotIn("<p>@testuser2</p>", html)

            self.assertIn('<button class="btn btn-primary btn-sm">Unfollow</button>', html)
    
    def test_users_followers_logged_in_other_profile(self):
        """Is the logged in user's followers shown? (logged in)"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            
            self.testuser1.followers.append(self.testuser2)
            db.session.commit()

            resp = c.get(f"/users/{self.testuser1.id}/followers")
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)

            self.assertNotIn('class="btn btn-outline-secondary">Edit Profile', html)

            self.assertIn("<p>@testuser2</p>", html)
            self.assertNotIn("<p>@testuser</p>", html)

            self.assertIn('<button class="btn btn-outline-primary btn-sm">Follow</button>', html)

    def test_users_followers_logged_in_self(self):
        """Is the logged in user's followers shown? (logged in)"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            
            self.testuser.followers.append(self.testuser2)
            db.session.commit()

            resp = c.get(f"/users/{self.testuser.id}/followers")
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)

            self.assertIn('class="btn btn-outline-secondary">Edit Profile', html)

            self.assertIn("<p>@testuser2</p>", html)
            self.assertNotIn("<p>@testuser1</p>", html)

            self.assertIn('<button class="btn btn-outline-primary btn-sm">Follow</button>', html)
     
    def test_add_follow_logged_in(self):
        """Can logged in user follow someone (logged in)"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/users/follow/{self.testuser1.id}")
            html = resp.get_data(as_text=True)

            # Check we are redirected
            self.assertEqual(resp.status_code, 302)
            # Check the testuser1 has successfully been followed
            self.assertIn(self.testuser1, self.testuser.following)
            self.assertEqual(len(self.testuser.following), 1)

    def test_stop_following_logged_in(self):
        """Can logged in user un-follow another user (logged in)"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Logged in user follows testuser1, should work if
            # test_add_follow_logged_in() succeeded
            c.post(f"/users/follow/{self.testuser1.id}")
            
            # Logged in user UN-follows testuser1
            resp = c.post(f"/users/stop-following/{self.testuser1.id}")

            self.assertEqual(resp.status_code, 302)
            # Check the testuser1 has successfully been UN-followed
            self.assertNotIn(self.testuser1, self.testuser.following)
            self.assertEqual(len(self.testuser.following), 0)

