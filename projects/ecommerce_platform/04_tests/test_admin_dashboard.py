import unittest
import requests
import json

BASE_URL = 'http://localhost:5000/api/admin'

class TestAdminDashboardAPI(unittest.TestCase):

    def test_admin_login(self):
        url = f'{BASE_URL}/login'
        headers = {'Content-Type': 'application/json'}
        payload = {
            'username': 'admin',
            'password': 'password'
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        self.assertEqual(response.status_code, 200)
        self.assertIn('tokens', response.json())

if __name__ == '__main__':
    unittest.main()