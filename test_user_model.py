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

USER_DATA_1 = { "email": "one@test.com",
            "username": "testuser1",
            "password": "HASHED_PASSWORD_1"}

USER_DATA_2 = { "email": "two@test.com",
            "username": "testuser2",
            "password": "HASHED_PASSWORD_2"}


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

    def test_user_model(self):
        """Does basic model work?"""

        u = User(**USER_DATA_1)

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr(self):
        """Does the repr method work as expected?"""

        u = User(**USER_DATA_1)
        db.session.add(u)
        db.session.commit()

        rep = f"<User #{u.id}: {u.username}, {u.email}>"

        # Convert repr of user to str for comparison of
        # string to string insead of User to string
        self.assertEqual(str(u),rep)
        self.assertNotEqual(u,rep)

    def test_is_following(self):
        """
        Does is_following detect when user1 is following user2
        Does is_following detect when user1 IS NOT following user2
        """

        user1 = User(**USER_DATA_1)
        user2 = User(**USER_DATA_2)
        db.session.add_all([user1, user2])
        db.session.commit()
        
        repr_follows = f"<Follows {user2.id}, {user1.id}>"

        # Check that user1 is not following user2
        self.assertNotIn(user2.id, user1.following)
        self.assertNotEqual(str(Follows.query.first()), repr_follows)
        # User1 starts following user2
        user1.following.append(user2)
        self.assertIn(user2, user1.following)
        self.assertEqual(str(Follows.query.first()), repr_follows)
        # User1 UNfollows user2
        user1.following.remove(user2)
        self.assertNotIn(user2, user1.following)
        self.assertNotEqual(str(Follows.query.first()), repr_follows)

    def test_is_followed(self):
        """
        Does is_following detect when user1 is followed by user2
        Does is_following detect when user1 IS NOT followed by user2
        """

        user1 = User(**USER_DATA_1)
        user2 = User(**USER_DATA_2)
        db.session.add_all([user1, user2])
        db.session.commit()

        repr_follows = f"<Follows {user1.id}, {user2.id}>"

        # Check that user1 is NOT being followed user2
        self.assertNotIn(user2.id, user1.followers)
        self.assertNotEqual(str(Follows.query.first()), repr_follows)

        # User1 starts being followed by user2
        user1.followers.append(user2)
        self.assertIn(user2, user1.followers)
        self.assertEqual(str(Follows.query.first()), repr_follows)
        
        # User1 STOPS being followed by user2
        user1.followers.remove(user2)
        self.assertNotIn(user2, user1.followers)
        self.assertNotEqual(str(Follows.query.first()), repr_follows)

    def test_create_user_success(self):
        """Does User.create successfully create a new user, given valid credentials"""

        t_email = "valid@test.com"
        t_username = "Valid_Test_User"
        t_password = "VALID_HASHED_PASS"
        
        u = User(
            email = t_email,
            username = t_username,
            password =  t_password
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(u, User.query.first())
        self.assertEqual(u.email, t_email)
        self.assertEqual(u.username, t_username)
        self.assertEqual(u.password, t_password)

    def test_create_user_fail(self):
        """
        Does User.create fail to create a new user if any of
        the validations (e.g. uniqueness, non-nullable fields) fail
        """
        g_email = "good@test.com"
        g_username = "Good_Test_User"
        g_password =  "GOOD_HASHED_PASS"

        v_email = "valid@test.com"
        v_username = "Valid_Test_User"
        v_password = "VALID_HASHED_PASS"
        
        # Add a valid user to check against for uniqueness
        u0 = User( email = v_email, username = v_username, password = v_password )
        db.session.add(u0)
        db.session.commit()
        # ------ Bad users ------ 
        # Missing 1 piece of data
        u1 = User(                  username = g_username, password = g_password )
        u2 = User( email = g_email,                        password = g_password )
        u3 = User( email = g_email, username = g_username,                       )
        # 1 pice of data is None 
        u4 = User( email = None,    username = g_username, password = g_password )
        u5 = User( email = g_email, username = None,       password = g_password )
        u6 = User( email = g_email, username = g_username, password = None       )
        # # Duplicate username    - UNIQUENESS ERROR
        u7 = User( email = v_email, username = g_username, password = g_password )
        # # Duplicate email       - UNIQUENESS ERROR
        u8 = User( email = g_email, username = v_username, password = g_password )

        # List of bad users to iterate through attempting to add users
        bad_users = [u1, u2, u3, u4, u5, u6, u7, u8]
        
        for u in bad_users:
            with self.assertRaises(ValueError):
                try:
                    db.session.add(u)
                    db.session.commit()
                except:
                    db.session.rollback()
                    # Raise ValueError (did not expect None
                    # for a given data piece, expected string)
                    raise ValueError
            # Should never gain more users beyond 1st valid user
            self.assertEqual(len(User.query.all()), 1)
        
    def test_user_authenticate_good_data(self):
        """
        Does User.authenticate return a valid user
        given a valid username/password
        """
        # Use signup to get a hashed password (which is in User.authenticate)
        User.signup( "testusername", "testemail@test.net", "TEST_PASSWORD", "" )

        user = User.query.first()
        self.assertEqual(user, User.authenticate(user.username, "TEST_PASSWORD"))
    
    def test_user_authenticate_bad_user(self):
        """ Does User.authenticate fail given a valid bad username """
        # Use signup to get a hashed password (which is in User.authenticate)
        User.signup( "testusername", "testemail@test.net", "TEST_PASSWORD", "" )

        user = User.query.first()
        # Returns false upon bad authentication
        self.assertFalse(User.authenticate("bad_username", "TEST_PASSWORD"))

    def test_user_authenticate_bad_pwd(self):
        """ Does User.authenticate fail given a valid bad username """
        # Use signup to get a hashed password (which is in User.authenticate)
        User.signup( "testusername", "testemail@test.net", "TEST_PASSWORD", "" )

        user = User.query.first()
        # Returns false upon bad authentication
        self.assertFalse(User.authenticate(user.username, "BAD_PASSWORD"))
        
        