import unittest
from app import app, db
from models import User

class TestApp(unittest.TestCase):

    def setUp(self):
        """Set up a testing client and configure the app."""
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///recipes_test' 
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection in forms during testing
        self.client = app.test_client()

        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_homepage(self):
        """Test the homepage route."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    def test_signup(self):
        """Test the signup route."""
        data = {
            'email': 'test@example.com',
            'password': 'password',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        response = self.client.post('/signup', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)
        # You can also check if the user was added to the database
        with app.app_context():
            user = User.query.filter_by(email='test@example.com').first()
            self.assertIsNotNone(user)
        
    def test_login(self):
        """Test the login route."""
        # Create a test user
        with app.app_context():
            user = User.signup(
                email='test@example.com',
                password='password',
                first_name='John',
                last_name='Doe'
            )
            db.session.commit()

        data = {
            'email': 'test@example.com',
            'password': 'password',
        }
        response = self.client.post('/login', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

if __name__ == '__main__':
    unittest.main()
