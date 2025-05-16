import unittest
from app import create_application
from app.extensions import db
from app.database import User
from app.config import TestingConfig


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_application(TestingConfig)
        self.app.config["WTF_CSRF_ENABLED"] = False  # Disable CSRF for testing
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_registration_success(self):
        response = self.client.post(
            "/register",
            data={
                "username": "newuser",
                "password": "test123",
                "confirm_password": "test123",
                "email": "new@example.com",
                "secret_question": "first_pet",
                "secret_answer": "fluffy",
                "terms": "y",
            },
            follow_redirects=True,
        )

        user = User.query.filter_by(username="newuser").first()
        self.assertIsNotNone(user)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Account created successfully", response.data)

    def test_registration_duplicate_username(self):
        user = User(username="duplicate", email="dup@example.com")
        user.set_password("secret")
        db.session.add(user)
        db.session.commit()

        response = self.client.post(
            "/register",
            data={
                "username": "duplicate",
                "password": "test123",
                "confirm_password": "test123",
                "email": "other@example.com",
                "secret_question": "birth_city",
                "secret_answer": "perth",
                "terms": "y",
            },
            follow_redirects=True,
        )

        self.assertIn(b"Username already exists", response.data)

    def test_login_success(self):
        user = User(username="testuser", email="test@example.com")
        user.set_password("test123")
        db.session.add(user)
        db.session.commit()

        response = self.client.post(
            "/login",
            data={"username": "testuser", "password": "test123"},
            follow_redirects=True,
        )

        self.assertIn(b"Dashboard", response.data)

    def test_login_failure_wrong_password(self):
        user = User(username="failuser", email="fail@example.com")
        user.set_password("rightpass")
        db.session.add(user)
        db.session.commit()

        response = self.client.post(
            "/login",
            data={"username": "failuser", "password": "wrongpass"},
            follow_redirects=True,
        )

        self.assertIn(b"Invalid username or password", response.data)

    def test_forgot_password_page_get(self):
        response = self.client.get("/forgot-password")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'name="username"', response.data)

    def test_forgot_password_valid_username(self):
        user = User(username="forgotuser", email="forgot@example.com")
        user.set_password("pass123")
        user.secret_question = "first_pet"
        user.set_secret_answer("fluffy")
        db.session.add(user)
        db.session.commit()

        response = self.client.post(
            "/forgot-password", data={"username": "forgotuser"}, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"What was the name of your first pet?", response.data)

    def test_forgot_password_invalid_username(self):
        response = self.client.post(
            "/forgot-password", data={"username": "nonexistent"}, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Username not found or no security question set", response.data)

    def test_forgot_password_user_without_secret_question(self):
        user = User(username="noquestion", email="noq@example.com")
        user.set_password("abc123")
        db.session.add(user)
        db.session.commit()

        response = self.client.post(
            "/forgot-password", data={"username": "noquestion"}, follow_redirects=True
        )

        self.assertIn(b"Username not found or no security question set", response.data)


if __name__ == "__main__":
    unittest.main()
