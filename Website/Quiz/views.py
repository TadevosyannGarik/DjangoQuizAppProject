from django.shortcuts import render, redirect
from . import forms, models
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from Teacher import models as TMODEL
from Student import models as SMODEL
from Teacher import forms as TFORM
from Student import forms as SFORM
from django.contrib.auth.models import User


def home_view(request):                             # проверяет, аутентифицирован ли пользователь, и перенаправляет его
    if request.user.is_authenticated:               # на страницу «после входа», если это так. Если пользователь не
        return HttpResponseRedirect('afterlogin')   # аутентифицирован, он отображает шаблон index.html.
    return render(request, 'quiz/index.html')


def is_teacher(user):                                           # Эта функция принимает объект пользователя и проверяет,
    return user.groups.filter(name='TEACHER').exists()          # принадлежит ли пользователь к группе «УЧИТЕЛЬ».


def is_student(user):                                           # Эта функция принимает объект пользователя и проверяет,
    return user.groups.filter(name='STUDENT').exists()          # принадлежит ли пользователь к группе «СТУДЕНТ».


def afterlogin_view(request):                          # Это представление сначала проверяет, является ли пользователь
    if is_student(request.user):                       # учеником или учителем, вызывая функции is_student и is_teacher.
        return redirect('student/student-dashboard')   # Если пользователь является студентом, он перенаправляет его
    elif is_teacher(request.user):                     # на страницу «студенческая панель». Если пользователь является
        accountapproval = TMODEL.Teacher.objects.all().filter(Users_id=request.user.id, Status=True)
        if accountapproval:                              # учителем, он проверяет, одобрена ли его учетная проверяя поле
            return redirect('teacher/teacher-dashboard') # «Статус» в модели TMODEL.Teacher. Если учетная запись одоб,
        else:                                            # она перенаправляет пользователя на страницу <Панель упр. учи>
            return render(request, 'teacher/teacher_wait_for_approval.html')
    else:                                               # Если учетная запись не утверждена, отображается шаблон
        return redirect('admin-dashboard')              # «teacher_wait_for_approval.html». Если пользователь не принад
#                                                       # ни к группе "СТУДЕНТ", ни к группе "ПРЕПОДАВАТЕЛЬ", он
#                                                       # перенаправляет его на страницу "админ-панель".


def adminclick_view(request):                           # Это представление проверяет, аутентифицирован ли пользователь,
    if request.user.is_authenticated:                   # и перенаправляет его на страницу «после входа», если это так.
        return HttpResponseRedirect('afterlogin')       # Если пользователь не аутентифицирован, он перенаправляет его
    return HttpResponseRedirect('adminlogin')           # на страницу «adminlogin».


@login_required(login_url='adminlogin')
def admin_dashboard_view(request):                                          # это предст. предоставляет статистику,
    dict = {                                                                # связанную с общим количеством студентов,
'total_student': SMODEL.Student.objects.all().count(),                      # преподавателей, курсов и вопросов в
'total_teacher': TMODEL.Teacher.objects.all().filter(Status=True).count(),  # приложении викторины. Он отображает шаблон
'total_course': models.Course.objects.all().count(),                        # «admin_dashboard.html» и передает
'total_question': models.Question.objects.all().count(),}                   # статистику в качестве контекста.
    return render(request, 'quiz/admin_dashboard.html', context=dict)


@login_required(login_url='adminlogin')                                    # это представление предоставляет статистику,
def admin_teacher_view(request):                                           # связанную с общим количеством учителей,
    dict = {                                                               # ожидающих утверждения учителей и общей
'total_teacher': TMODEL.Teacher.objects.all().filter(Status=True).count(),  # заработной платой утвержденных учителей Он
'pending_teacher': TMODEL.Teacher.objects.all().filter(Status=False).count(),  # отображает шаблон «admin_teacher.html»
'salary': TMODEL.Teacher.objects.all().filter(Status=True).aggregate(Sum('Salary'))['Salary__sum'],}
    return render(request, 'quiz/admin_teacher.html', context=dict)        # и передает статистику в качестве контекста.


@login_required(login_url='adminlogin')                           # в этом представлении отображается список всех
def admin_view_teacher_view(request):                             # утвержденных учителей в приложении викторины. Он
    teachers = TMODEL.Teacher.objects.all().filter(Status=True)   # извлекает список учителей из модели TMODEL.Teacher
    return render(request, 'quiz/admin_view_teacher.html', {'teachers': teachers}) # и отображает шаблон
#                                                                 # «admin_view_teacher.html», передавая список
#                                                                 # учителей в качестве контекста.


@login_required(login_url='adminlogin')                          # это представление позволяет администратору обновлять
def update_teacher_view(request, pk):                            # информацию профиля конкретного учителя. Он извлекает
    teacher = TMODEL.Teacher.objects.get(id=pk)                  # объекты учителя и пользователя, соответствующие
    user = TMODEL.User.objects.get(id=teacher.Users_id)           # заданному первичному ключу «pk», создает формы
    userForm = TFORM.TeacherUserForm(instance=user)              # для обновления информации о пользователе и учителе
    teacherForm = TFORM.TeacherForm(request.FILES, instance=teacher) # и отображает шаблон «update_teacher.html» с
    mydict = {'userForm': userForm, 'teacherForm': teacherForm} # формами в качестве контекста. Если метод запроса POST
    if request.method == 'POST':                               # и данные формы действительны, информация о пользователе
        userForm = TFORM.TeacherUserForm(request.POST, instance=user) # и учителе обновляется, а представление
        teacherForm = TFORM.TeacherForm(request.POST, request.FILES, instance=teacher) # перенаправляется на страницу
        if userForm.is_valid() and teacherForm.is_valid():          # «admin-view-teacher».
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            teacherForm.save()
            return redirect('admin-view-teacher')
    return render(request, 'quiz/update_teacher.html', context=mydict)


@login_required(login_url='adminlogin')                # этот код предоставляет администратору простой способ удалить
def delete_teacher_view(request, pk):                  # учителя и связанную с ним учетную запись пользователя в
    teacher = TMODEL.Teacher.objects.get(id=pk)        # приложении викторины. Использование декоратора @login_required
    user = User.objects.get(id=teacher.Users_id)       # помогает обеспечить доступ к этой функции только авторизованным
    user.delete()                                      # пользователям.
    teacher.delete()
    return HttpResponseRedirect('/admin-view-teacher')


@login_required(login_url='adminlogin')                                    # Эта функция извлекает всех учителей со
def admin_view_pending_teacher_view(request):                              # статусом False и отображает шаблон, который
    teachers = TMODEL.Teacher.objects.all().filter(Status=False)           # их отображает
    return render(request, 'quiz/admin_view_pending_teacher.html', {'teachers': teachers})


@login_required(login_url='adminlogin')                            # Эта функция получает форму зарплаты для
def approve_teacher_view(request, pk):                             # конкретного учителя и обновляет зарплату и
    teacherSalary = forms.TeacherSalaryForm()                      # статус учителя, если форма действительна. Если
    if request.method == 'POST':                                   # форма недействительна, она выводит сообщение на
        teacherSalary = forms.TeacherSalaryForm(request.POST)      # консоль. Если обновление прошло успешно, оно
        if teacherSalary.is_valid():                               # перенаправляет пользователя на страницу, на
            teacher = TMODEL.Teacher.objects.get(id=pk)            # которой отображаются ожидающие учителя
            teacher.Salary = teacherSalary.cleaned_data['salary']
            teacher.Status = True
            teacher.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/admin-view-pending-teacher')
    return render(request, 'quiz/salary_form.html', {'teacherSalary': teacherSalary})


@login_required(login_url='adminlogin')                          # Эта функция удаляет учителя и связанную с ним
def reject_teacher_view(request, pk):                            # учетную запись пользователя. Затем он перенаправляет
    teacher = TMODEL.Teacher.objects.get(id=pk)                  # пользователя на страницу, на которой отображаются
    Users = User.objects.get(id=teacher.Users_id)                # ожидающие учителя.
    Users.delete()
    teacher.delete()
    return HttpResponseRedirect('/admin-view-pending-teacher')


@login_required(login_url='adminlogin')                                # Эта функция извлекает всех учителей со статусом
def admin_view_teacher_salary_view(request):                           # True и отображает шаблон, отображающий их
    teachers = TMODEL.Teacher.objects.all().filter(Status=True)        # зарплаты
    return render(request, 'quiz/admin_view_teacher_salary.html', {'teachers': teachers})


@login_required(login_url='adminlogin')                               # Эта функция получает общее количество
def admin_student_view(request):                                      # студентов и отображает шаблон, который
    dict = {                                                          # его отображает.
        'total_student': SMODEL.Student.objects.all().count(),
    }
    return render(request, 'quiz/admin_student.html', context=dict)


@login_required(login_url='adminlogin')                               # Эта извлекает всех учащихся и отображает шаблон,
def admin_view_student_view(request):                                 # который их отображает.
    students = SMODEL.Student.objects.all()
    return render(request, 'quiz/admin_view_student.html', {'students': students})


@login_required(login_url='adminlogin')                                # это представление обновляет сведения об ученике
def update_student_view(request, pk):                                  # в системе. Это требует, чтобы пользователь
    student = SMODEL.Student.objects.get(id=pk)                        # вошел в систему как администратор. Он принимает
    user = SMODEL.User.objects.get(id=student.Users_id)                # объект запроса и идентификатор студента (pk) и
    userForm = SFORM.StudentUserForm(instance=user)                    # извлекает объекты студента и пользователя,
    studentForm = SFORM.StudentForm(request.FILES, instance=student)   # используя модель SMODEL. Он также создает два
    mydict = {'userForm': userForm, 'studentForm': studentForm}        # экземпляра формы для пользователя и ученика.
    if request.method == 'POST':                                       # Если метод запроса POST, он обновляет данные
        userForm = SFORM.StudentUserForm(request.POST, instance=user)  # данные пользователя и студента и сохраняет их.
        studentForm = SFORM.StudentForm(request.POST, request.FILES, instance=student)
        if userForm.is_valid() and studentForm.is_valid():             # В конце он перенаправляет пользователя на
            user = userForm.save()                                     # страницу «admin-view-student». В противном
            user.set_password(user.password)                           # случае отображает страницу update_student.html
            user.save()                                                # с формами пользователя и ученика в качестве
            studentForm.save()                                         # контекста
            return redirect('admin-view-student')
    return render(request, 'quiz/update_student.html', context=mydict)


@login_required(login_url='adminlogin')                  # Это представление удаляет учащегося из системы. Это требует,
def delete_student_view(request, pk):                    # чтобы пользователь вошел в систему как администратор. Он
    student = SMODEL.Student.objects.get(id=pk)          # принимает объект запроса и идентификатор студента (pk) и
    user = User.objects.get(id=student.Users_id)         # извлекает объекты студента и пользователя, используя модель
    user.delete()                                        # SMODEL. Он удаляет объекты пользователя и ученика и перенапр
    student.delete()                                     # пользователя на страницу «admin-view-student».
    return HttpResponseRedirect('/admin-view-student')


@login_required(login_url='adminlogin')                  # В этом представлении отображаются курсы, доступные в системе.
def admin_course_view(request):                          # Это требует, чтобы пользователь вошел в систему как
    return render(request, 'quiz/admin_course.html')     # администратор. Он принимает объект запроса и отображает
#                                                        # страницу 'admin_course.html'.


@login_required(login_url='adminlogin')                   # Этот вид добавляет новый курс в систему. Это требует, чтобы
def admin_add_course_view(request):                       # пользователь вошел в систему как администратор. Он принимает
    courseForm = forms.CourseForm()                       # объект запроса и создает экземпляр CourseForm. Если метод
    if request.method == 'POST':                          # запроса POST, он сохраняет экземпляр формы курса и перенапр
        courseForm = forms.CourseForm(request.POST)       # пользователя на страницу «admin-view-course». В противном
        if courseForm.is_valid():                         # случае отображается страница admin_add_course.html с формой
            courseForm.save()                             # курса в качестве контекста.
        else:
            print("form is invalid")
        return HttpResponseRedirect('/admin-view-course')
    return render(request, 'quiz/admin_add_course.html', {'courseForm': courseForm})


@login_required(login_url='adminlogin')     # В этом представлении отображается список курсов, доступных в системе. Это
def admin_view_course_view(request):        # требует, чтобы пользователь вошел в систему как администратор. Он
    courses = models.Course.objects.all()   # принимает объект запроса, извлекает все курсы с использованием модели
    return render(request, 'quiz/admin_view_course.html', {'courses': courses})  # моделей и отображает страницу
#                                           # «admin_view_course.html» с курсами в качестве контекста.


@login_required(login_url='adminlogin')                 # Этот вид удаляет курс из системы. Это требует, чтобы
def delete_course_view(request, pk):                    # пользователь вошел в систему как администратор. Он принимает
    course = models.Course.objects.get(id=pk)           # объект запроса и идентификатор курса (pk) и извлекает объект
    course.delete()                                     # курса, используя модель моделей. Он удаляет объект курса и
    return HttpResponseRedirect('/admin-view-course')   # перенаправляет пользователя на страницу «admin-view-course».


@login_required(login_url='adminlogin')                # В этом представлении отображаются вопросы, доступные в системе.
def admin_question_view(request):                      # Это требует, чтобы пользователь вошел в систему как администрат
    return render(request, 'quiz/admin_question.html') # Он приним объект запроса и отобр страницу 'admin_question.html'


@login_required(login_url='adminlogin')                 # Эта функция требует входа в систему и отображает страницу со
def admin_view_question_view(request):                  # списком всех курсов, доступных в приложении. Он предназначен
    courses = models.Course.objects.all()               # для использования администратором для просмотра и управления
    return render(request,'quiz/admin_view_question.html',{'courses': courses})  # вопросами, связанными с каждым курсом


@login_required(login_url='adminlogin')            # Эта функция также требует входа в систему и принимает идентификатор
def view_question_view(request, pk):               # курса (pk) в качестве входных данных. Он извлекает все вопросы,
    questions = models.Question.objects.all().filter(Course_id=pk) # связанные с данным идентификатором курса, и
    return render(request, 'quiz/view_question.html', {'questions': questions})  # и отображает страницу, на которой
#                                        # отображаются все вопросы. Он предназначен для использования
#                                        # администратором для просмотра и управления вопросами для определенного курса.


@login_required(login_url='adminlogin')            # Эта функция требует входа в систему и принимает в качестве входных
def delete_question_view(request, pk):             # данных идентификатор вопроса (pk).Он удаляет вопрос из базы данных
    question = models.Question.objects.get(id=pk)  # и перенаправляет пользователя на страницу admin_view_question_view
    question.delete()                              # Он предназначен для использования администратором для удаления вопр
    return HttpResponseRedirect('/admin-view-question')


@login_required(login_url='adminlogin')    # Эта функция требует входа в систему и принимает идентификатор студента (pk)
def admin_view_marks_view(request, pk):    # в качестве входных данных. Он извлекает все курсы, доступные в приложении
    courses = models.Course.objects.all()  # и отображает страницу, на которой отображаются все доступные курсы.Он также
    response = render(request, 'quiz/admin_view_marks.html', {'courses': courses}) # устанавливает файл cookie для
    response.set_cookie('student_id', str(pk))  # для идентификатора учащегося, который будет использоваться позже для
    return response                        # отображения оценок выбранного учащегося. Он предназначен для использования
#                                           # администратором для просмотра и управления оценками конкретного учащегося.


@login_required(login_url='adminlogin')                 # Эта функция требует входа в систему и принимает идентификатор
def admin_check_marks_view(request, pk):                # курса(pk)в качестве входных данных. Он извлекает идентификатор
    course = models.Course.objects.get(id=pk)           # студента из файла cookie, установленного предыдущей функцией,
    student_id = request.COOKIES.get('student_id')      # и извлекает все результаты данного курса и студента. Затем он
    student = SMODEL.Student.objects.get(id=student_id) # отображает страницу, на которой отображаются оценки учащегося
#                                                       # по данному курсу. Он предназначен для использования
    results = models.Result.objects.all().filter(Exam=course).filter(Students=student) # администратором для просмотра
    return render(request, 'quiz/admin_check_marks.html', {'results': results})      # оценок учащегося по определенному
#                                                       # курсу


def aboutus_view(request):                        # Эта функция отображает страницу, на которой отображается информация
    return render(request, 'quiz/aboutus.html')   # о приложении и создавших его разработчиках. Он не требует входа в
#                                                 # систему и может быть доступен любому


def contactus_view(request):                       # Эта функция отображает страницу, на которой отображается контактная
    sub = forms.ContactusForm()                    # форма. Если форма отправлена, она отправляет электронное письмо на
    if request.method == 'POST':                   # адрес электронной почты приложения с именем пользователя, адресом
        sub = forms.ContactusForm(request.POST)    # электронной почты и сообщением. Если сообщение электронной почты
        if sub.is_valid():                         # отправлено успешно,отображается страница,информирующая пользователя
            email = sub.cleaned_data['Email']      # об успешной отправке сообщения электронной почты. Он не требует
            name = sub.cleaned_data['Name']        # входа в систему и может быть доступен любому.
            message = sub.cleaned_data['Message']  #
            send_mail(str(name) + ' || ' + str(email), message, settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER,
                      fail_silently=False)
            return render(request, 'quiz/contactussuccess.html')
    return render(request, 'quiz/contactus.html', {'form': sub})
