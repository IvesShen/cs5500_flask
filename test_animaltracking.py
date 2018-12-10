import requests
import pytest
import json
import uuid
from requests.auth import HTTPBasicAuth

BASE_URL = "https://flask-animaltracking.herokuapp.com" 
name = "admin"
password = "admin"

@pytest.fixture(scope="session")
def token():
        path = "/login"
        url = BASE_URL + path
        r = requests.get(url, auth=(name,password))
        assert r.status_code == 200
        return r.json()['token']


class TestAnimalTracking:
	#test if we can ping the application
	def test_hell_world(self):
		r = requests.get(BASE_URL)
		assert r.status_code == 200
	
	#test if we can get the list of all users and return the user[0] as the admin user
	def test_findusers(self, token):
		path = "/user"
		url = BASE_URL + path
		r = requests.get(url, headers={'x-access-token' : token})
		assert r.status_code == 200
		assert r.json()['users'][0]['name'] == 'admin'
		assert r.json()['users'][0]['public_id'] == '41508482-5fa5-4a06-80f8-a5e886cf06c5'

	#test if one specific user exists and return its name, public_id, and admin status
	def test_oneuser(self, token):
		path = "/user/2754d17c-de4a-4d03-a586-3cb2d0a0f633"
		url = BASE_URL + path
		r = requests.get(url, headers={'x-access-token' : token})
		assert r.status_code == 200
		assert r.json()['user']['name'] == 'client'
		assert r.json()['user']['public_id'] == '2754d17c-de4a-4d03-a586-3cb2d0a0f633'
		assert r.json()['user']['admin'] == True

	#test if we can add a user to user list
	def test_postuser(self, token):
		path = "/user"
		url  = BASE_URL + path
		data = {"name" : "newClient"+uuid.uuid1().hex, "password" : "newClient"}
		r = requests.post(url, headers={'x-access-token' : token}, json=data)
		assert r.status_code == 200
		assert r.json()['message'] == 'New user created!'
			
	#test if we can promote to admin user
	def test_promote(self, token):
		path = "/user/promote/ce1e6146-e7d9-421e-88a6-9ca3fa35dfef"
		url = BASE_URL + path
		r = requests.put(url, headers={'x-access-token' : token})
		assert r.status_code == 200
		assert r.json()['message'] == 'The user has been promoted'

	#test if we can update user information
	def test_updateuser(self, token):
		path = "/user/ce1e6146-e7d9-421e-88a6-9ca3fa35dfef"
		url = BASE_URL + path
		payload = {"name" : "modified"}
		r = requests.put(url, json=payload, headers={'x-access-token' : token})
		assert r.status_code == 200
		assert r.json()['message'] == 'The user has been updated'

	#test if we can delete one user
	def test_deleteuser(self, token):
		path = "/user/485b24a5-4c59-4679-ad7c-3077a558697e"
                url = BASE_URL + path
                r = requests.delete(url, headers={'x-access-token' : token})
		assert r.status_code == 200
		assert r.json()['message'] == 'The user has been deleted'
		












