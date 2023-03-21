from django.db import models
from django.contrib.auth.models import User


class Teacher(models.Model):
    Users = models.OneToOneField(User, on_delete=models.CASCADE)
    ProfilePictures = models.ImageField(upload_to='ProfilePicture/Teacher/', null=True, blank=True)
    Address = models.CharField(max_length=40)
    Mobile = models.CharField(max_length=20, null=False)
    Status = models.BooleanField(default=False)
    Salary = models.PositiveIntegerField(null=True)

    @property
    def get_name(self):
        return self.Users.first_name+" "+self.Users.last_name

    @property
    def get_instance(self):
        return self

    def __str__(self):
        return self.Users.first_name