import  json

from django.test import TestCase, Client
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED

from .models import User


class UserTestCase(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.path = '/api/user/create'
        self.username = 'test_username'
        self.password = 'test_pass'
        self.data = json.dumps({
            'username': self.username,
            'password': self.password
        })

    def test_create_user(self):
        response = self.client.post(self.path, self.data, content_type='application/json')
        
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, self.username)


class AuthenticationApiTestCase(TestCase):
    def setUp(self):
        self.clinet = Client()
        self.username = 'test_username'
        self.password = 'test_pass'
        self.user = User(username = self.username)
        self.user.set_password(self.password)
        self.user.save()
        self.user_data = json.dumps({
            'username': self.username,
            'password': self.password
        })
        self.obtain_token_path = '/api/token/pair'
        self.refresh_token_path = '/api/token/refresh'
        self.verify_token_path = '/api/token/verify'
    
    def test_obtain_token_pair(self):
        response = self.clinet.post(self.obtain_token_path, self.user_data, content_type='application/json')
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIsNotNone(response_data['access'])
        self.assertIsNotNone(response_data['refresh'])
    
    def test_obtain_token_pair_with_no_user(self):
        data = json.dumps({
            'username': 'unexisting_user',
            'password': 'wrong_password'
        })
        response = self.clinet.post(self.obtain_token_path, data, content_type='application/json')

        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)
    
    def test_token_refresh(self):
        token_response = self.client.post(self.obtain_token_path, self.user_data, content_type='application/json')
        data = json.dumps({
            'refresh': json.loads(token_response.content).get('refresh')
        })

        response = self.client.post(self.refresh_token_path, data, content_type='application/json')
        response_data = json.loads(response.content)
        
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIsNotNone(response_data['access'])
        self.assertIsNotNone(response_data['refresh'])
        
    def test_verify_token(self):
        token_response = self.client.post(self.obtain_token_path, self.user_data, content_type='application/json')
        data = json.dumps({
            'token': json.loads(token_response.content).get('access')
        })
        
        response = self.client.post(self.verify_token_path, data, content_type='application/json')
        
        self.assertEqual(response.status_code, HTTP_200_OK)
    
    def test_verify_token_wrong_access_token(self):
        wrong_token = 'afkgpwokw[pegqfplbwlbw[bplpdndndd]]'
        data = json.dumps({
            'token': wrong_token
        })
        
        response = self.client.post(self.verify_token_path, data, content_type='application/json')
        
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)
