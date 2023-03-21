from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    Users = models.OneToOneField(User, on_delete=models.CASCADE)
    ProfilePicture = models.ImageField(upload_to='ProfilePicture/Student/', null=True, blank=True)
    Address = models.CharField(max_length=40, null=True)
    Mobile = models.CharField(max_length=20, null=False)

    @property
    def get_name(self):
        return self.Users.first_name + " " + self.Users.last_name

    @property
    def get_instance(self):
        return self

    def __str__(self):
        return self.Users.first_name


class Quiz(models.Model):
    name = models.CharField(max_length=255)
    time_limit = models.IntegerField()