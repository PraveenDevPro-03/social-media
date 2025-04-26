from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    twitter_handle = models.CharField(max_length=100, blank=True)
    facebook_token = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class SocialMediaPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.CharField(max_length=20, choices=[('twitter', 'Twitter'), ('facebook', 'Facebook')])
    text = models.TextField(max_length=280)
    scheduled_time = models.DateTimeField(blank=True, null=True)
    posted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.platform} post by {self.user.username} at {self.created_at}"