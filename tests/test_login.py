from instagram_scraper import InstagramScraper
import os, requests, json, unittest

LOGIN_URL = "https://www.instagram.com/accounts/login/ajax/"
TEST_USER = "test_account827"
TEST_PASS = "123Hotcrossbuns"

def login():
	login_text, login_page = validateUser()
	if login_text.get('authenticated') and login_page.status_code == 200:
		return True
	return False

def validateUser():
	s = requests.Session()
	s.headers.update({'Referer': "https://www.instagram.com"})
	req = s.get("https://www.instagram.com")
	s.headers.update({'X-CSRFToken': req.cookies['csrftoken']})
	login_data = {'username': TEST_USER, 'password': TEST_PASS}
	login = s.post(LOGIN_URL, data=login_data, allow_redirects=True)
	s.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
	s.close()
	return json.loads(login.text), login

class TestLogin(unittest.TestCase):
	#tests login, if user is authenticated and http status code is 200,
	#then login was successful
	def test_login(self):
		self.assertTrue(login())

if __name__ == '__main__':
	unittest.main()