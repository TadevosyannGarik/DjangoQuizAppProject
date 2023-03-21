from django.db import models
from Student.models import Student


class Course(models.Model):
    CourseName = models.CharField(max_length=50)
    QuestionNumber = models.PositiveIntegerField()
    TotalMarks = models.PositiveIntegerField()

    def __str__(self):
        return self.CourseName


class Question(models.Model):
    Cat = (('Option1', 'Option1'), ('Option2', 'Option2'), ('Option3', 'Option3'), ('Option4', 'Option4'))
    Course = models.ForeignKey(Course, on_delete=models.CASCADE)
    Marks = models.PositiveIntegerField()
    Question = models.CharField(max_length=600)
    PossiblyAnswer1 = models.CharField(max_length=200)
    PossiblyAnswer2 = models.CharField(max_length=200)
    PossiblyAnswer3 = models.CharField(max_length=200)
    PossiblyAnswer4 = models.CharField(max_length=200)
    Answer = models.CharField(max_length=200, choices=Cat)


class Result(models.Model):
    Students = models.ForeignKey(Student, on_delete=models.CASCADE)
    Exam = models.ForeignKey(Course, on_delete=models.CASCADE)
    Marks = models.PositiveIntegerField()
    Date = models.DateTimeField(auto_now=True)