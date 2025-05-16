import unittest
import json
from app.extensions import db
from app.database import User
from app import create_application

class FriendTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_application('app.config.TestingConfig')
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        self.client.testing = True
        
        # Create test database
        db.create_all()
        
        # Create test users
        self.user1 = User(username='testuser1', email='test1@example.com')
        self.user1.set_password('password1')
        
        self.user2 = User(username='testuser2', email='test2@example.com')
        self.user2.set_password('password2')
        
        db.session.add(self.user1)
        db.session.add(self.user2)
        db.session.commit()
        
        # Log in as user1
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.user1.id)
            sess['_fresh'] = True

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_search_users(self):
        """Test that user search API returns correct results"""
        with self.client as c:
            # Make sure we're logged in for the test
            with c.session_transaction() as sess:
                sess['_user_id'] = str(self.user1.id)
                sess['_fresh'] = True
            
            response = c.get('/search-users?query=testuser2')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertIn('users', data)
            self.assertGreaterEqual(len(data['users']), 1)
            
            found_user2 = False
            for user in data['users']:
                if user['username'] == 'testuser2':
                    found_user2 = True
                    self.assertFalse(user['is_friend'])
                    break
            
            self.assertTrue(found_user2, "testuser2 not found in search results")

    def test_add_friend(self):
        """Test adding a friend"""
        with self.client as c:
            # Make sure we're logged in for the test
            with c.session_transaction() as sess:
                sess['_user_id'] = str(self.user1.id)
                sess['_fresh'] = True
            
            response = c.post('/add-friend', 
                            json={'username': 'testuser2'},
                            content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('message', data)
            
            # Verify friendship was created in database
            user1 = User.query.filter_by(username='testuser1').first()
            user2 = User.query.filter_by(username='testuser2').first()
            self.assertTrue(user1.is_friend(user2))

    def test_remove_friend(self):
        """Test removing a friend"""
        # First add as friend
        user1 = User.query.filter_by(username='testuser1').first()
        user2 = User.query.filter_by(username='testuser2').first()
        user1.add_friend(user2)
        db.session.commit()
        
        with self.client as c:
            # Make sure we're logged in for the test
            with c.session_transaction() as sess:
                sess['_user_id'] = str(self.user1.id)
                sess['_fresh'] = True
            
            # Then test removal
            response = c.post('/remove-friend', 
                            json={'username': 'testuser2'},
                            content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('message', data)
            
            # Verify friendship was removed in database
            user1 = User.query.filter_by(username='testuser1').first()
            user2 = User.query.filter_by(username='testuser2').first()
            self.assertFalse(user1.is_friend(user2))

    def test_add_nonexistent_friend(self):
        """Test adding a friend that doesn't exist"""
        with self.client as c:
            # Make sure we're logged in for the test
            with c.session_transaction() as sess:
                sess['_user_id'] = str(self.user1.id)
                sess['_fresh'] = True
            
            response = c.post('/add-friend', 
                            json={'username': 'nonexistent'},
                            content_type='application/json')
            
            self.assertEqual(response.status_code, 404)
            data = json.loads(response.data)
            self.assertIn('error', data)

    def test_add_self_as_friend(self):
        """Test that a user cannot add themselves as a friend"""
        with self.client as c:
            # Make sure we're logged in for the test
            with c.session_transaction() as sess:
                sess['_user_id'] = str(self.user1.id)
                sess['_fresh'] = True
            
            response = c.post('/add-friend', 
                            json={'username': 'testuser1'},
                            content_type='application/json')
            
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()