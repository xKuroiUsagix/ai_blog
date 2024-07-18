import json
from datetime import date

from django.test import TestCase
from ninja_jwt.tokens import RefreshToken
from rest_framework.status import (
    HTTP_401_UNAUTHORIZED, HTTP_201_CREATED, HTTP_400_BAD_REQUEST,
    HTTP_200_OK
)
from rest_framework.test import APIClient
from freezegun import freeze_time

from user.models import User
from .helpers import ai_verify_safety, get_ai_response
from .constants import MAX_AI_RESPONSE_LENGTH
from .models import Post, Comment


class AiFunctionsTestCase(TestCase):
    def setUp(self):
        self.safe_messages = [
            'I think you have valid point on this topic.',
            'So relatable',
            'You are wrong actually. There is mistake on line 10 in your code.'
        ]
        self.unsafe_messages = [
            'You can kill yourself.',
            'kys'
        ]

    def test_ai_verify_safe_massage(self):
        safety_verification = [ai_verify_safety(msg) for msg in self.safe_messages]

        for is_safe in safety_verification:
            assert is_safe == True

    def test_ai_verify_unsafe_message(self):
        # This test doesn't work sometimes because of the way how Gemini analyses safety, 
        # but should work most of the time
        safety_verification = [ai_verify_safety(msg) for msg in self.unsafe_messages]

        for is_safe in safety_verification:
            print(is_safe)
            assert is_safe == False
    
    def test_get_ai_response(self):
        response = get_ai_response(self.safe_messages[0])

        assert response is not None
        assert len(response) <= MAX_AI_RESPONSE_LENGTH


class PostsApiNoAuthTestCase(TestCase):
    def setUp(self):
        self.post_data = {
            'title': 'Test post title',
            'content': 'Test post content'
        }
        self.api_client = APIClient()
    
    def test_create_post(self):
        response = self.api_client.post('/api/blog/create-post', self.post_data, format='json')
        
        assert response.status_code == HTTP_401_UNAUTHORIZED


class PostApiTestCase(TestCase):
    def setUp(self):
        self.user = User(username = 'test_username')
        self.user.set_password('test_pass')
        self.user.save()
        self.safe_post_data = {
            'title': 'Test post title',
            'content': 'Test post content'
        }
        self.unsafe_post_data = {
            'title': 'Test title',
            'content': 'I think certain people should be killed'
        }
        
        self.api_client = APIClient()
        self.access_token = str(RefreshToken.for_user(self.user).access_token)
        self.api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

    def test_create_safe_post(self):
        response = self.api_client.post('/api/blog/create-post', self.safe_post_data, format='json')
        
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.get().title, self.safe_post_data['title'])
    
    def test_create_unsafe_post(self):
        response = self.api_client.post('/api/blog/create-post', self.unsafe_post_data, format='json')

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(Post.objects.count(), 0)


class CommentApiTestCase(TestCase):
    def setUp(self):
        self.user = User(
            username = 'test_username',
            auto_post_reply = None
        )
        self.user.set_password('test_pass')
        self.user.save()
        self.post = Post.objects.create(
            title = 'Test post title',
            content = 'Test content',
            user = self.user
        )
        self.safe_comment_data = {
            'content': 'that was pretty useful'
        }
        self.unsafe_comment_data = {
            'content': 'You should be dead already'
        }
        self.api_client = APIClient()
        self.access_token = str(RefreshToken.for_user(self.user).access_token)
        self.api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
    
    def test_create_safe_comment(self):
        response = self.api_client.post(f'/api/blog/post/{self.post.id}/create-comment', self.safe_comment_data, format='json')
        
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.get().content, self.safe_comment_data['content'])
        self.assertEqual(self.post.comment.count(), 1)
    
    def test_create_unsafe_comment(self):
        response = self.api_client.post(f'/api/blog/post/{self.post.id}/create-comment', self.unsafe_comment_data, format='json')

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(Comment.objects.filter(is_blocked=True).count(), 1)


class AnalyticsApiTestCase(TestCase):
    def setUp(self):
        self.user = User(
            username = 'test_username',
            auto_post_reply = None
        )
        self.user.set_password('test_pass')
        self.user.save()

        self.api_client = APIClient()
        self.access_token = str(RefreshToken.for_user(self.user).access_token)
        self.api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

        self.post = Post.objects.create(
            title = 'Test post title',
            content = 'Test content',
            user = self.user
        )

        self.comment_content = 'Test comment content'
        self.generated_by_ai = 3
        self.days_amount = [21, 8, 11]
        self.days_blocked_amount = [5, 1, 3]
        self.days_dates = [
            date(year=2024, month=6, day=1),
            date(year=2024, month=6, day=2),
            date(year=2024, month=6, day=3)
        ]
        self.data = {
            'date_from': self.days_dates[0],
            'date_to': self.days_dates[-1]
        }

        self.comments_by_day = []
        for days, day_date in zip(self.days_amount, self.days_dates):
            freezer = freeze_time(str(day_date))
            freezer.start()
    
            self.comments_by_day.append(
                Comment.objects.bulk_create(self._create_comments_list(days))
            )

            freezer.stop()

        # Blocking some comments
        for comment_list, blocked_amount in zip(self.comments_by_day, self.days_blocked_amount):
            for i in range(blocked_amount):
                comment_list[i].is_blocked = True
                comment_list[i].save()
        
        # Mark some comments as generated by ai
        for comment_list in self.comments_by_day:
            reversed_comments = comment_list[::-1]
            counter = 0
            while counter < self.generated_by_ai:
                reversed_comments[counter].generated_by_ai = True
                reversed_comments[counter].save()
                counter += 1
    
    def _create_comments_list(self, count: int):
        comments = []

        for _ in range(count):
            comments.append(Comment(content=self.comment_content, user=self.user, post=self.post))
        
        return comments
    
    def test_analytics(self):
        response = self.api_client.get('/api/blog/analytics/comments-daily-breakdown', self.data, format='json')
        daily_analytics = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_200_OK)
        
        for record, day, comments, blocked_comments in \
            zip(daily_analytics, self.days_dates, self.days_amount, self.days_blocked_amount):
            self.assertEqual(record['day'], str(day))
            self.assertEqual(record['total_comments'], comments)
            self.assertEqual(record['blocked_comments'], blocked_comments)
    
    def test_analytics_excluding_ai(self):
        response = self.api_client.get('/api/blog/analytics/comments-daily-breakdown/exclude-ai', self.data, format='json')
        daily_analytics = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_200_OK)
        
        for record, day, comments, blocked_comments in \
            zip(daily_analytics, self.days_dates, self.days_amount, self.days_blocked_amount):
            self.assertEqual(record['day'], str(day))
            self.assertEqual(record['total_comments'], comments - self.generated_by_ai)
            self.assertEqual(record['blocked_comments'], blocked_comments)
    
    def test_analytics_ai_only(self):
        response = self.api_client.get('/api/blog/analytics/comments-daily-breakdown/ai-only', self.data, format='json')
        daily_analytics = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_200_OK)
        
        for record, day, comments, blocked_comments in \
            zip(daily_analytics, self.days_dates, self.days_amount, self.days_blocked_amount):
            self.assertEqual(record['day'], str(day))
            self.assertEqual(record['total_comments'], self.generated_by_ai)
            self.assertEqual(record['blocked_comments'], 0)
