from django.shortcuts import render
from . import forms
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from Quiz import models as QMODEL
from Student import models as SMODEL
from Quiz import forms as QFORM


def teacherclick_view(request):                            # Эта функция проверяет, аутентифицирован ли пользователь или
    if request.user.is_authenticated:                      # нет. Если пользователь аутентифицирован, он перенаправляет
        return HttpResponseRedirect('afterlogin')          # его на страницу «после входа в систему», в противном случае
    return render(request, 'teacher/teacherclick.html')    # он отображает шаблон «teacher/teacherclick.html».


def teacher_signup_view(request):
    userForm = forms.TeacherUserForm()
    teacherForm = forms.TeacherForm()
    mydict = {'userForm': userForm, 'teacherForm': teacherForm}      # Эта функция используется для управления процессом
    if request.method == 'POST':                                     # регистрации учителя. Сначала он создает экземпы
        userForm = forms.TeacherUserForm(request.POST)               # форм TeacherUserForm и TeacherForm, а затем
        teacherForm = forms.TeacherForm(request.POST, request.FILES) # добавляет их в контекстный словарь mydict. Если
        if userForm.is_valid() and teacherForm.is_valid():           # метод запроса POST, он проверяет формы и создает
            user = userForm.save()                                   # и создает новый экземпляр пользователя и учителя.
            user.set_password(user.password)                         # Затем он добавляет пользователя в группу УЧИТЕЛЬ
            user.save()                                              # и перенаправляет пользователя на страницу
            teacher = teacherForm.save(commit=False)                 # «teacherlogin». Если метод запроса не POST, он
            teacher.Users = user                                     # отображает шаблон «teacher/teachersignup.html» с
            teacher.save()                                           # контекстом mydict.
            my_teacher_group = Group.objects.get_or_create(name='TEACHER')
            my_teacher_group[0].user_set.add(user)
        return HttpResponseRedirect('teacherlogin')
    return render(request, 'teacher/teachersignup.html', context=mydict)


def is_teacher(user):                                   # Эта функция представляет собой пользовательскую функцию,
    return user.groups.filter(name='TEACHER').exists()  # которая принимает объект пользователя в качестве аргумента и
#                                                       # проверяет, принадлежит ли пользователь к группе «УЧИТЕЛЬ» или
#                                                       # нет. Возвращает True, если пользователь принадлежит к группе,
#                                                       # в противном случае возвращает False.


@login_required(login_url='teacherlogin')                                # Эта функция отображает информационную панель
@user_passes_test(is_teacher)                                            # для пользователя-учителя, которая включает
def teacher_dashboard_view(request):                                     # курсов, вопросов и студентов.
    dict = {

        'total_course': QMODEL.Course.objects.all().count(),
        'total_question': QMODEL.Question.objects.all().count(),
        'total_student': SMODEL.Student.objects.all().count()
    }
    return render(request, 'teacher/teacher_dashboard.html', context=dict)


@login_required(login_url='teacherlogin')                   # Эта функция отображает шаблон для управления экзаменами
@user_passes_test(is_teacher)                               # учителем.
def teacher_exam_view(request):
    return render(request, 'teacher/teacher_exam.html')


@login_required(login_url='teacherlogin')     # Эта функция извлекает все курсы из базы данных и отображает шаблон .
@user_passes_test(is_teacher)                 # «teacher/teacher_view_exam.html» с набором запросов курсов в качестве
def teacher_view_exam_view(request):          # контекста
    courses = QMODEL.Course.objects.all()     #
    return render(request, 'teacher/teacher_view_exam.html', {'courses': courses})


@login_required(login_url='teacherlogin')          # Эта функция принимает первичный ключ (pk) в качестве параметра,
@user_passes_test(is_teacher)                      # извлекает соответствующий объект курса из базы данных, удаляет его
def delete_exam_view(request, pk):                 # и перенаправляет на страницу «учитель/учитель-просмотр-экзамен».
    course = QMODEL.Course.objects.get(id=pk)
    course.delete()
    return HttpResponseRedirect('/teacher/teacher-view-exam')


@login_required(login_url='adminlogin')          # Эта функция отображает шаблон для пользователя-учителя для управления
def teacher_question_view(request):              # вопросами.
    return render(request, 'teacher/teacher_question.html')


@login_required(login_url='teacherlogin')                 # Эта функция используется для добавления нового вопроса.
@user_passes_test(is_teacher)                             # создает экземпляр формы QuestionForm и отображает шаблон
def teacher_add_question_view(request):                   # «teacher/teacher_add_question.html». Если метод запроса POST
    questionForm = QFORM.QuestionForm()                   # он проверяет форму и сохраняет новый экземпляр вопроса. Он
    if request.method == 'POST':                          # также устанавливает соответствующий курс для вопроса на
        questionForm = QFORM.QuestionForm(request.POST)   # основе выбранного курса из формы. Если форма недействительна
        if questionForm.is_valid():                       # она печатает сообщение об ошибке.
            question = questionForm.save(commit=False)
            course = QMODEL.Course.objects.get(id=request.POST.get('courseID'))
            question.Course = course
            question.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/teacher/teacher-view-question')
    return render(request, 'teacher/teacher_add_question.html', {'questionForm': questionForm})


@login_required(login_url='teacherlogin')                 # Эта функция извлекает все курсы из базы данных и отображает
@user_passes_test(is_teacher)                             # шаблон «teacher/teacher_view_question.html» с набором
def teacher_view_question_view(request):                  # запросов курсов в качестве контекста.
    courses = QMODEL.Course.objects.all()
    return render(request, 'teacher/teacher_view_question.html', {'courses': courses})


@login_required(login_url='teacherlogin')                 # Эта функция принимает первичный ключ (pk) в качестве
@user_passes_test(is_teacher)                             # параметра, извлекает из базы данных все вопросы, относящиеся
def see_question_view(request, pk):                       # к соответствующему объекту курса, и отображает шаблон
    questions = QMODEL.Question.objects.all().filter(Course_id=pk) # 'teacher/see_question.html' с набором запросов
    return render(request, 'teacher/see_question.html', {'questions': questions}) # вопросов в качестве контекста.


@login_required(login_url='teacherlogin')                 # Эта функция принимает первичный ключ (pk) в качестве
@user_passes_test(is_teacher)                             # параметра, извлекает соответствующий объект вопроса из базы
def remove_question_view(request, pk):                    # данных, удаляет его и перенаправляет на страницу
    question = QMODEL.Question.objects.get(id=pk)         # «учитель/учитель-просмотр-вопрос»
    question.delete()
    return HttpResponseRedirect('/teacher/teacher-view-question')