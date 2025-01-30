from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import os


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False,
                              null=False, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    store = models.ForeignKey(
        'orders.Store', on_delete=models.CASCADE, blank=True, null=True)

    username = models.CharField(
        max_length=150, unique=True, blank=True, null=True)
    phone_number = models.CharField(
        unique=True, blank=True, null=True, max_length=10)

    zip_code = models.CharField(max_length=12, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    def path_to_avatar(self, filename):
        return 'avatars/temp/avatar.jpg'

    avatar = models.ImageField(
        upload_to=path_to_avatar, blank=True, null=True, verbose_name='avatar')

    def __str__(self):
        return self.email

class AccountSettings(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    addr = models.CharField()

    class Meta:
        verbose_name_plural = 'Account Settings'

    def __str__(self):
        return self.user.email

@receiver(post_save, sender=CustomUser)
def update_file_path(instance, created, **kwargs):
    if created and instance.avatar and 'temp' in instance.avatar.path:
        initial_path = instance.avatar.path
        new_path = settings.MEDIA_ROOT + f'/avatars/{instance.id}/avatar.jpg'
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        os.rename(initial_path, new_path)
        instance.avatar.name = f'avatars/{instance.id}/avatar.jpg'
        instance.save()
