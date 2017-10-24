import unittest
import flaskRestful
import json

class TestFlaskApi(unittest.TestCase):
    def setUp(self):
        self.app = flaskRestful.app.test_client()

    def test_hello_world(self):
        response = self.app.get('/')
        self.assertEqual(json.loads(response.get_data()), {'hello': 'world'})


if __name__ == "__main__":
    unittest.main()
