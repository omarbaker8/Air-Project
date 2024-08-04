from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    AVATAR_CHOICES = [(str(i), f'Avatar {i}') for i in range(17)]  # 0 to 15

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.CharField(max_length=2, choices=AVATAR_CHOICES, default='0')

    def __str__(self):
        return f'{self.user.username} Profile'

    def get_avatar_url(self):
        return f'/static/images/avatars/{self.avatar}.png'


