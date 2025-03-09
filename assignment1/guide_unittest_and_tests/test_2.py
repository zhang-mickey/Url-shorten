import unittest
import requests
import time


class URLShortenerAPITestCase(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:8000/"

    def setUp(self):
        """init"""
        self.headers = {'Content-Type': 'application/json'}

    def test_create_short_link(self):
        """create short link"""
        print("--- Create short link ----")
        data = {
            "value": "https://en.wikipedia.org/wii/Bitstream",
            "expiry_time": "2000",
            "user_id": "abc"
        }
        response = requests.post(self.BASE_URL, json=data, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        response_json = response.json()
        self.assertIn('id', response_json)  # 确保返回的 JSON 包含 ID
        self.short_id = response_json['id']  # 保存短链接 ID 以便后续测试

    def test_get_short_link(self):
        """get short link"""
        print("--- Get short link ----")
        self.test_create_short_link()
        if not hasattr(self, 'short_id'):
            self.skipTest("Skipping test because short_id was not created.")

        response = requests.get(f"{self.BASE_URL}{self.short_id}?user_id=abc")
        self.assertEqual(response.status_code, 301)
        response_json = response.json()
        self.assertEqual(response_json['value'], "https://en.wikipedia.org/wii/Bitstream")

    def test_update_short_link(self):
        """update link"""
        print("--- Update short link ----")
        self.test_get_short_link()
        if not hasattr(self, 'short_id'):
            self.skipTest("Skipping test because short_id was not created.")

        update_data = {
            "url": "https://en.wikipedia.org/wiki/Caproni"
        }
        response = requests.put(f"{self.BASE_URL}{self.short_id}?user_id=abc", json=update_data, headers=self.headers)
        self.assertEqual(response.status_code, 200)

        # Verify the update by GET request
        response = requests.get(f"{self.BASE_URL}{self.short_id}?user_id=abc")
        self.assertEqual(response.status_code, 301)
        response_json = response.json()
        self.assertEqual(response_json['value'], "https://en.wikipedia.org/wiki/Caproni")

    def test_delete_short_link(self):
        """delete short link"""
        print("--- Delete short link ----")
        self.test_update_short_link()
        if not hasattr(self, 'short_id'):
            self.skipTest("Skipping test because short_id was not created.")

        response = requests.delete(f"{self.BASE_URL}{self.short_id}?user_id=abc")
        self.assertEqual(response.status_code, 204)

        # Verify the deletion by GET request
        response = requests.get(f"{self.BASE_URL}{self.short_id}?user_id=abc")
        self.assertEqual(response.status_code, 404)  # get after delete, return 404

    def test_create_multiple_users(self):
        """test multiple users create short links"""
        print("--- Multiple users create short link ----")
        data_1 = {
            "value": "https://en.wikipedia.org/wiki/Dijkstra's_algorithm",
            "expiry_time": "2000",
            "user_id": "abc"
        }
        data_2 = {
            "value": "https://en.wikipedia.org/wiki/Dijkstra's_algorithm",
            "expiry_time": "2000",
            "user_id": "guest"
        }

        # First user creation
        response_1 = requests.post(self.BASE_URL, json=data_1, headers=self.headers)
        self.assertEqual(response_1.status_code, 201)
        response_1_json = response_1.json()
        short_id_1 = response_1_json['id']

        # Second user creation
        response_2 = requests.post(self.BASE_URL, json=data_2, headers=self.headers)
        self.assertEqual(response_2.status_code, 201)
        response_2_json = response_2.json()
        short_id_2 = response_2_json['id']

        # Verify different short IDs for different users
        self.assertNotEqual(short_id_1, short_id_2)

    def test_expire_short_link(self):
        """test expired link"""
        data = {
            "value": "https://en.wikipedia.org/wiki/Dijkstra's_algorithm",
            "expiry_time": "1",  # expiry time after 1 s
            "user_id": "abc"
        }
        response = requests.post(self.BASE_URL, json=data, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        response_json = response.json()
        short_id = response_json['id']

        time.sleep(10)  # wait for 10s to be sure the link has been expired

        # Verify the short link has expired by GET request
        response = requests.get(f"{self.BASE_URL}{short_id}?user_id=abc")
        self.assertEqual(response.status_code, 404)  # if link is expired, return 404

    def test_delete_all_links(self):
        """delete all links"""
        data = {
            "value": "https://en.wikipedia.org/wiki/Dijkstra's_algorithm",
            "expiry_time": "2000",
            "user_id": "abc"
        }

        # create links
        response = requests.post(self.BASE_URL, json=data, headers=self.headers)
        self.assertEqual(response.status_code, 201)

        # delete all links
        response = requests.delete(self.BASE_URL)
        self.assertEqual(response.status_code, 404)

        # Verify that all links are deleted
        response = requests.get(self.BASE_URL)
        self.assertEqual(response.status_code, 404)  # delete all then return 404


if __name__ == "__main__":
    unittest.main()
