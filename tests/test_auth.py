import unittest
from flask import session
from app.extensions import db
from app.database import User
from app import create_application


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_application('app.config.TestingConfig')
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        # Disable CSRF protection for testing
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        # Enable session in tests
        self.client.testing = True

        # Create test database
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_successful_registration(self):
            user = User(username='testuser', email='test@example.com')
            user.set_password('test123')
            db.session.add(user)
            db.session.commit()

            current_user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(current_user)
            self.assertTrue(current_user.check_password('test123'))

    def test_successful_login(self):
        user = User(username='testlogin', email='login@example.com')
        user.set_password('pass123')
        db.session.add(user)
        db.session.commit()

        response = self.client.post('/login', data={
            'username': 'testlogin',
            'password': 'pass123',
            'remember': 'y'
        }, follow_redirects=True)

        # Check for successful login - could be redirected to dashboard
        self.assertEqual(response.status_code, 200)
        # Check if any of these indicators of success are present
        self.assertTrue(
            b'Dashboard' in response.data or 
            b'Logout' in response.data or
            b'Welcome' in response.data
        ) 

    
    def test_failed_login_wrong_password(self):
        user = User(username='wrongpass', email='fail@example.com')
        user.set_password('correctpass')
        db.session.add(user)
        db.session.commit()

        # Test login with wrong password and check response
        with self.client as c:
            response = c.post('/login', data={
                'username': 'wrongpass',
                'password': 'wrongpass'
            }, follow_redirects=True)
            
            # Check if still on login page (failed login)
            self.assertIn(b'Login', response.data)
            # Look for error message in various places
            html_data = response.data.decode('utf-8')
            failed_login = (
                'Invalid username or password' in html_data or
                'Login failed' in html_data or
                'Invalid credentials' in html_data
            )
            self.assertTrue(failed_login, "Login failure message not found")

    def test_registration_existing_username(self):
        user = User(username='duplicate', email='dup@example.com')
        user.set_password('pass123')
        db.session.add(user)
        db.session.commit()

        # Test registration with duplicate username
        with self.client as c:
            response = c.post('/register', data={
                'username': 'duplicate',
                'password': 'pass456',
                'email': 'another@example.com',
                'confirm_password': 'pass456',
                'secret_question': 'first_pet',
                'secret_answer': 'test',
                'terms': 'y'
            }, follow_redirects=True)
            
            # Check for duplicate username error
            html_data = response.data.decode('utf-8')
            duplicate_error = (
                'Username already exists' in html_data or
                'Username is already taken' in html_data or
                'already in use' in html_data
            )
            self.assertTrue(duplicate_error, "Duplicate username error not found")


if __name__ == '__main__':
    unittest.main()