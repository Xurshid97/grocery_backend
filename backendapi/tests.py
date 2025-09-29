from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser12345678", password="secret")

    def test_model_str(self):
        self.assertEqual(str(self.user), "testuser")

    def test_raqam_field(self):
        # raqam should default to username
        self.assertEqual(self.user.raqam, "12345678")
