import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from application import create_app, db
from application.models.user import User
from application.models.post import Post
from application.models.note import Note
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='test')
        u.set_password('1234')
        self.assertFalse(u.check_password('4321'))
        self.assertTrue(u.check_password('1234'))


    def test_follow(self):
        u1 = User(username='user1', email='aa@aa.com')
        u2 = User(username='user2', email='bb@bb.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u2.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'user2')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'user1')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_password_recovery(self):
        u1 = User(username='user1', email='aa@aa.com')
        db.session.add(u1)
        db.session.commit()

        token = u1.get_reset_password_token()
        verified_user = User.verify_reset_password_token(token)
        self.assertEqual(u1, verified_user)

    def test_add_note(self):
        u1 = User(username='user1', email='aa@aa.com')
        db.session.add(u1)
        db.session.commit()
        self.assertEqual(u1.notes.count(), 0)

        u1.add_note('test title', 'test description')
        self.assertEqual(u1.notes.count(), 1)
        self.assertEqual(u1.notes.filter_by(id=1).first().title, 'test title')


        

if __name__ == '__main__':
    unittest.main(verbosity=2)