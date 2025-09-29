from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import CustomUser

class CustomUserTest(TestCase):
    def setUp(self):
        User = get_user_model()  # ✅ This gets the correct user model
        self.user = User.objects.create_user(username="testuser", password="secret")
        self.custom_user = CustomUser.objects.create(name="Test Object", owner=self.user)

    def test_model_str(self):
        self.assertEqual(str(self.custom_user), "Test Object")

    def test_object_owner(self):
        self.assertEqual(self.custom_user.owner.username, "testuser")
