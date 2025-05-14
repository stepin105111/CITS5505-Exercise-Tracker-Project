import unittest
from app.database import db, User
from app.app import app


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_successful_registration(self):
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('test123')
            db.session.add(user)
            db.session.commit()

            current_user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(current_user)
            self.assertTrue(current_user.check_password('test123'))

    def test_successful_login(self):
        with app.app_context():
            user = User(username='testlogin', email='login@example.com')
            user.set_password('pass123')
            db.session.add(user)
            db.session.commit()

        response = self.app.post('/login', data={
            'username': 'testlogin',
            'password': 'pass123'
        }, follow_redirects=True)

        self.assertIn(b'Dashboard', response.data) 

    
    def test_failed_login_wrong_password(self):
        with app.app_context():
            user = User(username='wrongpass', email='fail@example.com')
            user.set_password('correctpass')
            db.session.add(user)
            db.session.commit()

        response = self.app.post('/login', data={
            'username': 'wrongpass',
            'password': 'wrongpass'
        }, follow_redirects=True)

        self.assertIn(b'Invalid username or password', response.data)

    def test_registration_existing_username(self):
        with app.app_context():
            user = User(username='duplicate', email='dup@example.com')
            user.set_password('pass123')
            db.session.add(user)
            db.session.commit()

        response = self.app.post('/register', data={
            'username': 'duplicate',
            'password': 'pass456',
            'email': 'another@example.com'
        }, follow_redirects=True)

        self.assertIn(b'Username already exists', response.data)


if __name__ == '__main__':
    unittest.main()