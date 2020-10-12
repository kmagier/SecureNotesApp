import unittest
import sys
import os
import io
import json
from werkzeug.datastructures import FileStorage
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from application import create_app, db
from application.models.user import User
from application.models.post import Post
from application.models.note import Note
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class NoteModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_subscribe(self):
        u1 = User(username='user1', email='aa@aa.com')
        db.session.add(u1)
        db.session.commit()
        self.assertEqual(u1.notes.count(), 0)

        note = Note(title='test title', description='test description')
        db.session.add(note)
        db.session.commit()
        self.assertEqual(note.is_subscribing(u1), 0)
        note.subscribe_note(u1)
        self.assertEqual(note.is_subscribing(u1), 1)

    def test_unsubscribe(self):
        u1 = User(username='user1', email='aa@aa.com')
        db.session.add(u1)
        note = Note(title='test title', description='test description')
        db.session.add(note)
        db.session.commit()

        note.subscribe_note(u1)
        self.assertEqual(note.is_subscribing(u1), 1)
        note.unsubscribe_note(u1)
        self.assertEqual(note.is_subscribing(u1), 0)

    def test_edit(self):
        note = Note(title='test title', description='test description')
        db.session.add(note)
        db.session.commit()

        self.assertEqual(note.title, 'test title')
        note.edit_note(title='new title', description='new description')
        self.assertEqual(note.title, 'new title')
        self.assertEqual(note.description, 'new description')

    def test_upload(self):
        note = Note(title='test title', description='test description')
        db.session.add(note)
        db.session.commit()

        self.assertIsNone(note.attachment_hash)
        self.assertIsNone(note.file_path)
        self.assertIsNone(note.org_attachment_filename)

        input_content = json.dumps(dict(content='test'), indent=4).encode('utf-8')

        test_file = FileStorage(
            stream=io.BytesIO(input_content),
            filename='test.pdf',
            content_type='application/json',
        )

        note.upload_attachment(test_file)
        self.assertIsNotNone(note.attachment_hash)
        self.assertIsNotNone(note.file_path)
        self.assertIsNotNone(note.org_attachment_filename)
        self.assertEqual(note.org_attachment_filename, 'test.pdf')

    def test_edit_with_attachment(self):
        note = Note(title='test title', description='test description')
        db.session.add(note)
        db.session.commit()

        self.assertIsNone(note.attachment_hash)
        self.assertIsNone(note.file_path)
        self.assertIsNone(note.org_attachment_filename)

        input_content = json.dumps(dict(content='test'), indent=4).encode('utf-8')

        test_file = FileStorage(
            stream=io.BytesIO(input_content),
            filename='test.pdf',
            content_type='application/json',
        )

        note.edit_note(title='new title', description='new description', attachment=test_file)
        self.assertIsNotNone(note.attachment_hash)
        self.assertIsNotNone(note.file_path)
        self.assertIsNotNone(note.org_attachment_filename)
        self.assertEqual(note.org_attachment_filename, 'test.pdf')


if __name__ == '__main__':
    unittest.main(verbosity=2)