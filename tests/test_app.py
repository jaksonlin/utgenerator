import unittest
from app import app

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_generate_unittest(self):
        response = self.app.post('/generate_unittest', json={'java_code': 'public class HelloWorld { public static void main(String[] args) { System.out.println("Hello, world!"); } }'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('unittest', response.json)

if __name__ == '__main__':
    unittest.main()