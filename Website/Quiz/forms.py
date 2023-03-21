from django import forms
from django.contrib.auth.models import User
from . import models


class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500, widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))


class TeacherSalaryForm(forms.Form):
    salary = forms.IntegerField()


class CourseForm(forms.ModelForm):
    class Meta:
        model = models.Course
        fields = ['CourseName', 'QuestionNumber', 'TotalMarks']


class QuestionForm(forms.ModelForm):
    courseID = forms.ModelChoiceField(queryset=models.Course.objects.all(), empty_label="Course Name", to_field_name="id")

    class Meta:
        model = models.Question
        fields = ['Marks', 'Question', 'PossiblyAnswer1', 'PossiblyAnswer2', 'PossiblyAnswer3', 'PossiblyAnswer4', 'Answer']
        widgets = {'question': forms.Textarea(attrs={'rows': 3, 'cols': 50})}