from instagram.client import InstagramAPI
import pytest

access_token = "1452718484.7aaf07a.512deb47397e4bffb6e18da65f11270e"
client_secret = "67a95b790d714163bf039758690a9b60"
client_id = "7aaf07aaa882491eb4c73bbdc94fa455"

api = InstagramAPI(access_token=access_token, client_secret=client_secret, client_id=client_id)

def test_string_equal():
	assert get_string() == "([User: oalcaraz.09, User: kellynieh], None)"

def test_string_equal2():
	assert get_string() == "([User: oalcaraz.09, User: kellynieh], Noe)"	

def get_string():
	liked_media = str(api.user_follows())
	return liked_media

'''
RUN:
py.test a6_pytest.py

- Calvin Teng

'''