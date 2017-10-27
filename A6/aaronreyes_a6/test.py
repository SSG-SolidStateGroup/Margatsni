import unittest
from redirecting import app

class FlaskTestCase(unittest.TestCase):

    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/')
        self.assertEqual(response.status_code, 302)

if __name__ == "__main__":
    unittest.main()
