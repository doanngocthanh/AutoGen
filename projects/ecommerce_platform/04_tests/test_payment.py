import unittest
import requests
import json
import os

BASE_URL = 'http://localhost:5000/payment'

class TestPaymentAPI(unittest.TestCase):

    def test_create_vnpay_payment(self):
        url = f'{BASE_URL}/vnpay/create_payment'
        headers = {'Content-Type': 'application/json'}
        payload = {
            'amount': 100,
            'orderId': 'ORDER123'
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        self.assertEqual(response.status_code, 200)
        self.assertIn('url', response.json())

    def test_create_momo_payment(self):
        url = f'{BASE_URL}/momo/create_payment'
        headers = {'Content-Type': 'application/json'}
        payload = {
            'amount': 100,
            'orderId': 'ORDER123'
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        self.assertEqual(response.status_code, 200)
        self.assertIn('payUrl', response.json())

    # Add tests for vnpay_return, vnpay_ipn, momo_return, momo_ipn when you have a running server

if __name__ == '__main__':
    unittest.main()
