from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime


class User(AbstractUser):
    pass

class Profile(models.Model):
    target = models.ForeignKey('User', on_delete=models.CASCADE, related_name='folowers')
    follower = models.ForeignKey('User', on_delete=models.CASCADE, related_name='targets')

class Post(models.Model):
    content = models.TextField()
    likes = models.IntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_posts")
    timestamp = models.DateTimeField(auto_now_add=True)

    """def __str__(self):
        return self.author + " posted: \"" + self.content + "\""
        """

class Follower(models.Model):
    username = models.CharField(max_length=150)
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers") #user being followed

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likers")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="liked_post")
