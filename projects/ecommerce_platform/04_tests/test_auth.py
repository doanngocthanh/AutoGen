import unittest
import requests
import json

BASE_URL = 'http://localhost:5000/api/auth'

class TestAuthAPI(unittest.TestCase):

    def test_register_user(self):
        url = f'{BASE_URL}/register'
        headers = {'Content-Type': 'application/json'}
        payload = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123'
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json())

    def test_login_user(self):
        url = f'{BASE_URL}/login'
        headers = {'Content-Type': 'application/json'}
        payload = {
            'email': 'testuser@example.com',
            'password': 'password123'
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json())

    def test_get_logged_in_user(self):
        # First, register and login to get a token
        register_url = f'{BASE_URL}/register'
        register_headers = {'Content-Type': 'application/json'}
        register_payload = {
            'username': 'testuser2',
            'email': 'testuser2@example.com',
            'password': 'password123'
        }
        register_response = requests.post(register_url, headers=register_headers, data=json.dumps(register_payload))
        self.assertEqual(register_response.status_code, 200)
        token = register_response.json()['token']

        # Then, use the token to get the logged-in user
        get_user_url = f'{BASE_URL}'
        get_user_headers = {'x-auth-token': token}
        get_user_response = requests.get(get_user_url, headers=get_user_headers)
        self.assertEqual(get_user_response.status_code, 200)
        self.assertEqual(get_user_response.json()['email'], 'testuser2@example.com')

if __name__ == '__main__':
    unittest.main()
