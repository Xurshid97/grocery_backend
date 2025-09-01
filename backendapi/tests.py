from django.test import TestCase
from django.contrib.auth.models import User
from .models import CustomUser

# Create your tests here.
class CustomUserTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="secret")
        self.custom_user = CustomUser.objects.create(name="Test Object", owner=self.user)

    def test_model_str(self):
        self.assertEqual(str(self.custom_user), "Test Object")

    def test_object_owner(self):
        self.assertEqual(self.custom_user.owner.username, "testuser")
