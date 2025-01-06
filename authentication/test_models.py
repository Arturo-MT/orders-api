from django.test import TestCase
from django.contrib.auth import get_user_model
from authentication.models import CustomUser
from django.core.files.uploadedfile import SimpleUploadedFile

class CustomUserModelTest(TestCase):

    def setUp(self):
        CustomUser.objects.all().delete()
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            email='testuser@example.com',
            password='password123',
            first_name='Test',
            last_name='User',
            username='testuser',
            phone_number='1234567890',
            avatar=SimpleUploadedFile('test.jpg', b'file_content', content_type='image/jpeg')
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'testuser@example.com')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.phone_number, '1234567890')
        self.assertTrue(self.user.check_password('password123'))

    def test_user_str(self):
        self.assertEqual(str(self.user), 'testuser@example.com')

    def test_email_unique(self):
        with self.assertRaises(Exception):
            self.user_model.objects.create_user(
                email='testuser@example.com',
                password='password123',
                first_name='Test2',
                last_name='User2',
                username='testuser2',
                phone_number='0987654321'
            )

    def test_username_unique(self):
        with self.assertRaises(Exception):
            self.user_model.objects.create_user(
                email='testuser2@example.com',
                password='password123',
                first_name='Test2',
                last_name='User2',
                username='testuser',
                phone_number='0987654321'
            )

    def test_phone_number_unique(self):
        with self.assertRaises(Exception):
            self.user_model.objects.create_user(
                email='testuser2@example.com',
                password='password123',
                first_name='Test2',
                last_name='User2',
                username='testuser2',
                phone_number='1234567890'
            )
    
    def test_user_avatar_path(self):
        self.assertEqual(self.user.avatar.path, f'/code/media/avatars/{self.user.id}/avatar.jpg')
