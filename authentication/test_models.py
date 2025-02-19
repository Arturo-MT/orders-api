from django.test import TestCase
from django.contrib.auth import get_user_model
from authentication.models import CustomUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.utils import IntegrityError


class CustomUserModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_model = get_user_model()

        cls.user, created = cls.user_model.objects.get_or_create(
            email='testuser1@example.com',
            defaults={
                "password": "password123",
                "first_name": "Test",
                "last_name": "User",
                "username": "testuser",
                "phone_number": "1234567890",
                "avatar": SimpleUploadedFile('test.jpg', b'file_content', content_type='image/jpeg'),
            }
        )

        if created:
            cls.user.set_password("password123")
            cls.user.save()

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'testuser1@example.com')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.phone_number, '1234567890')
        self.assertTrue(self.user.check_password('password123'))

    def test_user_str(self):
        self.assertEqual(str(self.user), 'testuser1@example.com')

    def test_email_unique(self):
        with self.assertRaises(IntegrityError):
            self.user_model.objects.create(
                email='testuser1@example.com',
                password='password123',
                first_name='Test2',
                last_name='User2',
                username='testuser1',
                phone_number='0987654321'
            )

    def test_username_unique(self):
        with self.assertRaises(IntegrityError):
            self.user_model.objects.create(
                email='testuser3@example.com',
                password='password123',
                first_name='Test2',
                last_name='User2',
                username='testuser',
                phone_number='0987654221'
            )

    def test_phone_number_unique(self):
        with self.assertRaises(IntegrityError):
            self.user_model.objects.create(
                email='testuser4@example.com',
                password='password123',
                first_name='Test2',
                last_name='User2',
                username='testuser3',
                phone_number='1234567890'
            )

    def test_user_avatar_path(self):
        expected_path = f'/code/app/media/avatars/{self.user.id}/avatar.jpg'
        self.assertEqual(self.user.avatar.path, expected_path)
