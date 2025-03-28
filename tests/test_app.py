# tests/test_app.py
import unittest
from application import app  # import your Flask app here

class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
