from django.shortcuts import render, redirect, reverse
from . import forms, models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from datetime import date, timedelta
from Quiz import models as QMODEL
from Teacher import models as TMODEL
from django.shortcuts import render
from .models import Quiz


def studentclick_view(request):                           # Эта функция проверяет, аутентифицирован ли пользователь уже,
    if request.user.is_authenticated:                     # и перенаправляет его на страницу «после входа». Если
        return HttpResponseRedirect('afterlogin')         # пользователь не прошел проверку подлинности, он отображает
    return render(request, 'student/studentclick.html')   # шаблон «studentclick.html».


def student_signup_view(request):                                     # Эта функция обрабатывает процесс регистрации
    userForm = forms.StudentUserForm()                                # студентов. Он создает экземпляр StudentUserForm
    studentForm = forms.StudentForm()                                 # и StudentForm. Если данные формы действительны,
    mydict = {'userForm': userForm, 'studentForm': studentForm}       # создается новый пользователь, устанавливается
    if request.method == 'POST':                                      # устанавливается пароль и сохраняются данные
        userForm = forms.StudentUserForm(request.POST)                # формы учащегося. Он также добавляет нового
        studentForm = forms.StudentForm(request.POST, request.FILES)  # пользователя в группу «СТУДЕНТ». После успешной
        if userForm.is_valid() and studentForm.is_valid():            # регистрации функция перенаправляет пользователя
            user = userForm.save()                                    # на страницу входа в систему.
            user.set_password(user.password)
            user.save()
            student = studentForm.save(commit=False)
            student.Users = user
            student.save()
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
        return HttpResponseRedirect('studentlogin')
    return render(request, 'student/studentsignup.html', context=mydict)


def is_student(user):  # Это вспомогательная функция, которая принимает экземпляр пользователя в качестве входных данных
    return user.groups.filter(name='STUDENT').exists()  # и возвращает логическое значение, указывающее, принадлежит ли
#                      # пользователь к группе «СТУДЕНТ». Эта функция используется в качестве декоратора для функций
#                      # student_dashboard_view и student_exam_view, чтобы гарантировать, что только аутентифицированные
#                      # пользователи, принадлежащие к группе «STUDENT», могут получить доступ к этим представлениям.


@login_required(login_url='studentlogin')  # Эта функция извлекает некоторую статистику, связанную с приложением
@user_passes_test(is_student)              # викторины, например общее количество курсов и вопросов, и отображает шаблон
def student_dashboard_view(request):       # «student_dashboard.html».
    dict = {

        'total_course': QMODEL.Course.objects.all().count(),
        'total_question': QMODEL.Question.objects.all().count(),
    }
    return render(request, 'student/student_dashboard.html', context=dict)


@login_required(login_url='studentlogin')      # Эта функция извлекает все доступные курсы и отображает шаблон
@user_passes_test(is_student)                  # «student_exam.html» с данными курсов.
def student_exam_view(request):
    courses = QMODEL.Course.objects.all()
    return render(request, 'student/student_exam.html', {'courses': courses})


@login_required(login_url='studentlogin')                           # Эта функция также требует, чтобы пользователь
@user_passes_test(is_student)                                       # вошел в систему как студент, и проверяет, ли
def start_exam_view(request, pk):                                   # пользователь студентом, используя те же декораторы
    course = QMODEL.Course.objects.get(id=pk)                       # @login_required и @user_passes_test. Функция
    questions = QMODEL.Question.objects.all().filter(Course=course) # принимает запрос и первичный ключ (pk) в качестве
    if request.method == 'POST':                                    # в качестве аргументов и извлекает конкретный курс
        pass                                                        # базы данных. Если метод запроса — POST, функция
    response = render(request, 'student/start_exam.html', {'course': course, 'questions': questions})
    response.set_cookie('course_id', course.id) # ничего не делает, в противном случае она возвращает обработанную HTML-
    return response                             # страницу с подробностями курса и вопросами, на которые студент должен
#                                               # ответить. Эта функция также устанавливает файл cookie, содержащий
#                                               # идентификатор курса, для использования в будущем.


@login_required(login_url='studentlogin')                               # эта функция также требует, чтобы пользователь
@user_passes_test(is_student)                                           # вошел в систему как студент, и проверяет,
def calculate_marks_view(request):                                      # является ли пользователь студентом, используя
    if request.COOKIES.get('course_id') is not None:                    # те же декораторы @login_required и
        course_id = request.COOKIES.get('course_id')                    # @user_passes_test. Функция извлекает
        course = QMODEL.Course.objects.get(id=course_id)                # идентификатор курса из файла cookie,
#                                                                       # установленного в предыдущей функции, извлекает
        total_marks = 0                                                 # курс из базы данных и вычисляет общие оценки
        questions = QMODEL.Question.objects.all().filter(Course=course) # за экзамен на основе выбранных ответов
        for i in range(len(questions)):                                 # учащегося. Затем функция создает новый объект
                                                                        # Result в базе данных с оценками учащегося,
            selected_ans = request.COOKIES.get(str(i + 1))              # экзаменом и идентификатором учащегося. Затем
            actual_answer = questions[i].Answer                         # функция перенаправляет учащегося на страницу
            if selected_ans == actual_answer:                           # просмотра результатов.
                total_marks = total_marks + questions[i].Marks
        student = models.Student.objects.get(Users_id=request.user.id)
        result = QMODEL.Result()
        result.Marks = total_marks
        result.Exam = course
        result.Students = student
        result.save()

        return HttpResponseRedirect('view-result')


@login_required(login_url='studentlogin')    # эта функция требует, чтобы пользователь вошел в систему как студент,
@user_passes_test(is_student)                # используя декоратор @login_required с указанным URL-адресом для входа.
def view_result_view(request):               # Он также проверяет, является ли пользователь студентом, используя
    courses = QMODEL.Course.objects.all()    # декоратор @user_passes_test с определенной функцией.Функция извлекает все
    return render(request, 'student/view_result.html', {'courses': courses}) # курсы из базы данных и
#                                            # возвращает обработанную HTML-страницу с курсами, доступными
#                                            # для просмотра студентом их результатов.


@login_required(login_url='studentlogin')                            # эта функция check_marks_view также требует,
@user_passes_test(is_student)                                        # чтобы пользователь вошел в систему как студент,
def check_marks_view(request, pk):                                   # и проверяет, является ли пользователь студентом,
    course = QMODEL.Course.objects.get(id=pk)                        # используя те же декораторы @login_required и
    student = models.Student.objects.get(Users_id=request.user.id)   # @user_passes_test. Функция принимает запрос
    results = QMODEL.Result.objects.all().filter(Exam=course).filter(Students=student) # и первичный ключ (pk)
    return render(request, 'student/check_marks.html', {'results': results}) # в качестве аргументов и извлекает конкрет
#                                                                    # курс из базы данных. Эта функция также
#                                                                    # также извлекаетиз базы данных сведения о учащемся
#                                                                    # и результаты этого курса и возвращает обработанну
#                                                                    # HTML-страницу с результатами.


@login_required(login_url='studentlogin')   # Третья функция student_marks_view также требует, чтобы пользователь вошел
@user_passes_test(is_student)               # в систему как студент, и проверяет, является ли пользователь студентом,
def student_marks_view(request):            # используя те же декораторы @login_required и @user_passes_test. Функция
    courses = QMODEL.Course.objects.all()   # извлекает все курсы из базы данных и возвращает обработанную HTML-страницу
    return render(request, 'student/student_marks.html', {'courses': courses}) # с курсами, доступными для учащегося
                                            # просмотра своих оценок.


