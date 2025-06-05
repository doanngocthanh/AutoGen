import unittest
import requests
import json

BASE_URL = 'http://localhost:5000'

class TestProductAPI(unittest.TestCase):

    def test_create_product(self):
        url = f'{BASE_URL}/products'
        headers = {'Content-Type': 'application/json'}
        payload = {
            'name': 'Test Product',
            'description': 'Test Description',
            'category_id': 1,
            'price': 99.99,
            'image_url': 'http://example.com/image.jpg'
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], 'Test Product')

    def test_get_all_products(self):
        url = f'{BASE_URL}/products'
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_get_product_by_id(self):
        # Assuming there's a product with ID 1
        url = f'{BASE_URL}/products/1'
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], 1)

    def test_update_product(self):
        url = f'{BASE_URL}/products/1'
        headers = {'Content-Type': 'application/json'}
        payload = {
            'name': 'Updated Product',
            'description': 'Updated Description',
            'price': 129.99
        }
        response = requests.put(url, headers=headers, data=json.dumps(payload))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'Updated Product')

    def test_delete_product(self):
        url = f'{BASE_URL}/products/1'
        response = requests.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Product deleted successfully!')

class TestCategoryAPI(unittest.TestCase):

    def test_create_category(self):
        url = f'{BASE_URL}/categories'
        headers = {'Content-Type': 'application/json'}
        payload = {
            'name': 'Test Category',
            'description': 'Test Category Description',
            'image_url': 'http://example.com/category.jpg'
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], 'Test Category')

    def test_get_all_categories(self):
        url = f'{BASE_URL}/categories'
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_get_category_by_id(self):
        # Assuming there's a category with ID 1
        url = f'{BASE_URL}/categories/1'
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], 1)

    def test_update_category(self):
        url = f'{BASE_URL}/categories/1'
        headers = {'Content-Type': 'application/json'}
        payload = {
            'name': 'Updated Category',
            'description': 'Updated Category Description'
        }
        response = requests.put(url, headers=headers, data=json.dumps(payload))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Category updated successfully')

    def test_delete_category(self):
        url = f'{BASE_URL}/categories/1'
        response = requests.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Category deleted successfully')

if __name__ == '__main__':
    unittest.main()
