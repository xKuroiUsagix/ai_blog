from django.test import TestCase

from .helpers import ai_verify_safety, get_ai_response
from .constants import MAX_AI_RESPONSE_LENGTH


class AiFunctionsTestCase(TestCase):
    def setUp(self):
        self.safe_messages = [
            'I think you have valid point on this topic.',
            'So relatable',
            'You are wrong actually. There is mistake on line 10 in your code.'
        ]
        self.unsafe_messages = [
            'You can kill yourself.',
            'kys',
            'dummest thing I\'ve ever heard'
        ]

    def test_ai_verify_safe_massage(self):
        safety_verification = [ai_verify_safety(msg) for msg in self.safe_messages]

        for is_safe in safety_verification:
            assert is_safe == True

    def test_ai_verify_unsafe_message(self):
        safety_verification = [ai_verify_safety(msg) for msg in self.unsafe_messages]

        for is_safe in safety_verification:
            assert is_safe == False
    
    def test_get_ai_response(self):
        response = get_ai_response(self.safe_messages[0])

        assert response is not None
        assert len(response) <= MAX_AI_RESPONSE_LENGTH
