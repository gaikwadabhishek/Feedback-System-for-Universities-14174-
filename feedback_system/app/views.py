import json
from django.shortcuts import render
from django.conf.urls import include
from django.template import loader
from .models import Student, Faculty,Department, TeacherSubject, FeedbackForm, Question, QuestionType, FeedbackResponse, Tag, TextualResponse
from .forms import SignUpForm,LogInForm,CreateNewForm, Subject
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from app.db_api.authentication import authenticate_role
from app.db_api.logic import collect_feedback
from django.contrib.auth import login as user_login
from app.decorators import student_required, faculty_required, auditor_required, coordinator_required
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .final_new import get_sentiment, get_tags

from django.db.models import Count,Sum,Avg,IntegerField,Case,When
from django.shortcuts import render_to_response


ACADEMICS = QuestionType.objects.get(title='Academics')
INFRASTRUCTURE = QuestionType.objects.get(title='Infrastructure')
FACULTY = QuestionType.objects.get(title='Faculty')

@login_required
def home(request):
    return render(request, 'base-vuetify.html')

@student_required
def student_dashboard(request):
	feedbackforms = FeedbackForm.objects.filter(is_active=True, is_published=True)
	context = {
		'numberofforms':len(feedbackforms),
		'feedbackforms':feedbackforms
	}
	return render(request, 'student_dashboard_new_new.html', context)

@student_required
def ajax_student_dashboard(request):
	feedbackforms = FeedbackForm.objects.filter(is_active=True, is_published=True)
	student = request.user.student
	context = {}	
	for form in feedbackforms:
		responses = FeedbackResponse.objects.filter(student=student,question__feedback_form=form)
		count = responses.count()
		if count == 0:
			context['form'+str(form.id)] = 'Urgent'
		elif count < 50:
			context['form'+str(form.id)] = 'Incomplete'
		else:
			context['form'+str(form.id)] = 'Complete'
	return JsonResponse(context)

@student_required
def student_profile(request):
	return render(request, 'student_profile_new.html')

@student_required
def events(request):
	return render(request, 'events.html')

@faculty_required
def faculty_dashboard(request):
	#formid
	context = {}
	forms = list(FeedbackForm.objects.filter(is_published=True))
	teacher_subjects = list(TeacherSubject.objects.filter(teacher=request.user.faculty))
	for form in forms:
		context[form] = {}
		for teacher_subject in teacher_subjects:
			context[form][teacher_subject.subject] = {}
			avg = list(FeedbackResponse.objects.filter(teacher_subject=teacher_subject,question__feedback_form=form).values('teacher_subject').annotate(avg =Avg('answer',output_field=IntegerField())))
			for data in avg:
				temp =None
				for key,value in data.items():
					if(key == 'avg'):
						temp =value
				data['counter_avg'] =5-temp
			context[form][teacher_subject.subject]['overall'] = avg

			context[form][teacher_subject.subject]['responses'] = {}
			context[form][teacher_subject.subject]['strength']=set()
			context[form][teacher_subject.subject]['weakness']=set()
			responses = list(FeedbackResponse.objects.filter(teacher_subject=teacher_subject,question__feedback_form=form))
			for response in responses:
				question = response.question
				#print(question.tag.tag_title)
				context[form][teacher_subject.subject]['responses'][question] = {}
				temp = list(FeedbackResponse.objects.filter(question=question).values('question').annotate(avg =Avg('answer')))
				context[form][teacher_subject.subject]['responses'][question]['overall'] = temp[0]['avg']
				for data in temp:
					if(float(data['avg']) > 3.5):#not working
						context[form][teacher_subject.subject]['strength'].add(question.tag)
					else:
						context[form][teacher_subject.subject]['weakness'].add(question.tag)
				scores= {}
				for i in range(1,6):
						scores[i] = FeedbackResponse.objects.filter(teacher_subject=teacher_subject,question=question,answer =i).count()
				
				context[form][teacher_subject.subject]['responses'][question]['scores'] = scores

	#print(context)

	return render_to_response( 'faculty_dashboard.html',locals())


@faculty_required
def faculty_profile(request):
	return render(request, 'faculty_profile_new.html')

@auditor_required
def auditor_profile(request):
	return render(request, 'auditor_profile.html')


def auditor_dashboard(request):

	context = {}
	forms   = list(FeedbackForm.objects.filter(is_published=True))
	departments = list( Department.objects.all() )
	for form in forms:
		context[form] = {}
		types = list(QuestionType.objects.all())
		types_overall_rating=list(FeedbackResponse.objects.filter(question__feedback_form =form).values('question__type__title').annotate(avg =Avg('answer')))
		for type_ in types_overall_rating:
			type_['avg']=round(((type_['avg']/5)*100),2)
		context[form]['types_overall_rating'] =types_overall_rating
		
	
	
	print(context)
		


	return render_to_response('auditor_dashboard.html',locals())

	'''
	infrastructure_data =list(FeedbackResponse.objects.filter(question__type__title="Infrastructure").values('question').annotate(dsum=Sum('answer')))
	academics_data = list(FeedbackResponse.objects.filter(question__type__title="Academics").values('question').annotate(dsum=Sum('answer')))
	for data in infrastructure_data:
		question_id = data['question']
		data['question'] = (Question.objects.get(id=question_id)).text

	for data in academics_data:
		question_id = data['question']
		data['question'] = (Question.objects.get(id=question_id)).text

	#print(infrastructure_data)
	context = {'infrastructure':infrastructure_data ,'academics':academics_data}
	
	def student_count(form):
	department = list( Department.objects.all() )
	types = list()
	student_count_deptwise ={}
	for dept in department:
		print(dept.name)
		student_count_deptwise[dept.name] = len(FeedbackResponse.objects.filter(question__feedback_form__title = 'Feedback - I',student__classroom__department__name =dept.name))


	
	'''

@coordinator_required
def coordinator_dashboard(request):
	forms = FeedbackForm.objects.all()
	context = {
		'forms':forms
	}
	return render(request, 'coordinator_dashboard.html', context)

@coordinator_required
def publish_form(request, formid):
	form = FeedbackForm.objects.get(pk=formid)
	form.is_published = True
	form.save()
	return redirect('coordinator_dashboard')

@coordinator_required
def activate_form(request, formid):
	form = FeedbackForm.objects.get(pk=formid)
	form.is_active = True
	form.save()
	return redirect('coordinator_dashboard')

@coordinator_required
def deactivate_form(request, formid):
	form = FeedbackForm.objects.get(pk=formid)
	form.is_active = False
	form.save()
	return redirect('coordinator_dashboard')

@coordinator_required
def copy_form(request, formid):
	form = FeedbackForm.objects.get(pk=formid)
	form.pk = None
	form.title = form.title + ' - Copy'
	form.is_active = False
	form.is_published = False
	form.save()
	for question in Question.objects.filter(feedback_form=FeedbackForm.objects.get(pk=formid)):
		question.pk = None
		question.feedback_form = form
		question.save()
	return redirect('coordinator_dashboard')

@coordinator_required
def ajax_delete_question(request):
	formid = request.POST['formid']
	qid = request.POST['qid']
	Question.objects.get(pk=qid, feedback_form=FeedbackForm.objects.get(pk=formid)).delete()
	return JsonResponse({'success':'true'});

@student_required
def ajax_text_response(request):
	print('here')
	form = FeedbackForm.objects.get(pk=request.POST['formid'])
	student = Student.objects.get(pk=request.POST['student'])
	text = request.POST['text']
	type = QuestionType.objects.get(title=request.POST['type'])

	text_response = TextualResponse(
		student=student,
		type=type,
		answer=text,
		feedback_form=form
	)
	text_response.save()
	print('text response saved')

	sentiment = get_sentiment(text)

	return JsonResponse({'sentiment':sentiment})

@coordinator_required
def ajax_predict_tags(request):
	text = request.POST['text']
	tag = get_tags(text)
	print("Tag id is", tag)
	return JsonResponse({'tag':tag})


@coordinator_required
def edit_form_title(request):
	formid = request.POST['formid']
	title = request.POST['title']
	form = FeedbackForm.objects.get(pk=formid)
	form.title = title
	form.save()
	return JsonResponse({'success':'true'})

@coordinator_required
def edit_form(request, formid=None):
	if formid:
		form = FeedbackForm.objects.get(pk=formid)
	else:
		form = FeedbackForm(title='Blank Form')
	form.save()
	questions = Question.objects.filter(feedback_form=form)
	acadquestions = questions.filter(type=ACADEMICS)
	infraquestions = questions.filter(type=INFRASTRUCTURE)
	facultyquestions = questions.filter(type=FACULTY)
	tags = Tag.objects.all()
	context = {
		'form':form,
		'acadquestions':acadquestions,
		'infraquestions':infraquestions,
		'facultyquestions':facultyquestions,
		'tags':tags
	}
	return render(request, 'edit_questions.html', context)

@coordinator_required
def coordinator_profile(request):
	return render(request, 'coordinator_profile.html')

@coordinator_required
def create_form(request):
	if request.method == 'POST':
		form = CreateNewForm(request.POST)
		if form.is_valid():
			title = form.cleaned_data['title']
			new_form = FeedbackForm(title=title)
			new_form.save()
			return redirect('add_questions',formid=new_form.id)
	else:
		form = CreateNewForm()
	return render(request, 'create_form.html', {'form':form})

@coordinator_required
def add_questions(request,formid):
	curr_form = FeedbackForm.objects.get(pk=formid)
	context = {
		'curr_form':curr_form
	}
	return render(request, 'add_questions.html', context)

@coordinator_required
def ajax_add_questions(request):
	print(request.POST)
	data = request.POST
	q = Question(
		text=data['text'],
		tag=Tag.objects.get(pk=data['tagid']),
		type=QuestionType.objects.get(title=data['type']),
		feedback_form=FeedbackForm.objects.get(pk=data['form'])
	)
	q.save()
	
	context = {}
	return redirect('edit_form',data['form'])

@coordinator_required
def edit_form_question(request):
	print(request.POST)
	data = request.POST
	q = Question(
		text=data['text'],
		tag=Tag.objects.get(pk=data['tagid']),
		type=QuestionType.objects.get(title=data['type']),
		feedback_form=FeedbackForm.objects.get(pk=data['formid'])
	)
	q.save()
	
	context = {}
	return redirect('edit_form',data['formid'])


@student_required
def feedback_faculty(request,formid):	
	curr_user = request.user
	teachings = TeacherSubject.objects.filter(classroom=curr_user.student.classroom)
	courses = {teaching.subject: teaching.teacher for teaching in teachings}
	feedbackform = FeedbackForm.objects.get(pk=formid)
	questions = Question.objects.filter(feedback_form=feedbackform)
	facultyquestions = questions.filter(type=FACULTY)
	context = {
		'courses': courses,
		'facultyquestions':facultyquestions
	}
	return render(request, 'feedback_faculty.html', context)

@student_required
def student_feedback(request, formid):
	print('in student_feedback',formid)
	curr_user = request.user
	feedbackform = FeedbackForm.objects.get(pk=formid)
	teachings = TeacherSubject.objects.filter(classroom=curr_user.student.classroom)
	courses = {teaching.subject: teaching.teacher for teaching in teachings}
	questions = Question.objects.filter(feedback_form=feedbackform)
	acadquestions = questions.filter(type=ACADEMICS)
	infraquestions = questions.filter(type=INFRASTRUCTURE)
	
	context = {
		'form':feedbackform,
		'courses': courses,
		'acadquestions':acadquestions,
		'infraquestions':infraquestions,
	}

	return render(request, 'feedback_new.html', context)

@student_required
def student_feedback_response_set(request):
	q_id = request.GET.get('q_id',None)
	s_id = request.GET.get('s_id',None)
	a_val = request.GET.get('a_val',None)

	question = Question.objects.filter(pk=q_id).first()
	student = Student.objects.filter(pk=s_id).first()
	a_val = int(a_val)

	try:
		fr = FeedbackResponse.objects.get(student=student,question=question)
	except:
		fr = FeedbackResponse.objects.create(student=student,question=question,answer=a_val)
	fr.answer = a_val
	print(fr.answer)
	fr.save()
	
	return JsonResponse({
		'success':'success'
	})

@student_required
def student_feedback_response_get(request):
	q_id = request.GET.get('q_id',None)
	s_id = request.GET.get('s_id',None)
	
	question = Question.objects.filter(pk=q_id).first()
	student = Student.objects.filter(pk=s_id).first()
	
	try:
		fr = FeedbackResponse.objects.get(student=student,question=question)
		ansval = fr.answer
		print(ansval)
		return JsonResponse({
			'ans':ansval
		})
	except:
		return JsonResponse({
			'ans':0
		})

@student_required
def student_feedback_faculty_response_set(request):
	print('\n\n\n\n\n\n\n SFFRS called \n\n\n\n\n\n\n')

	q_id = request.GET.get('q_id',None)
	s_id = request.GET.get('s_id',None)
	f_id = request.GET.get('f_id',None)
	sub_id = request.GET.get('sub_id',None)
	a_val = request.GET.get('a_val',None)

	question = Question.objects.filter(pk=q_id).first()
	student = Student.objects.filter(pk=s_id).first()
	faculty = Faculty.objects.filter(pk=f_id).first()
	subject = Subject.objects.filter(pk=sub_id).first()

	teacher_subject = TeacherSubject.objects.filter(classroom=student.classroom,teacher=faculty,subject=subject).first()

	print(q_id, f_id, s_id, sub_id, a_val, question, student, faculty, subject, teacher_subject)
	
	a_val = int(a_val)

	try:
		fr = FeedbackResponse.objects.get(student=student,question=question,teacher_subject=teacher_subject)
	except:
		fr = FeedbackResponse.objects.create(student=student,question=question,teacher_subject=teacher_subject,answer=a_val)
	fr.answer = a_val
	print(fr.answer)
	fr.save()
	
	return JsonResponse({
		'success':'success'
	})

@student_required
def student_feedback_faculty_response_get(request):
	q_id = request.GET.get('q_id',None)
	s_id = request.GET.get('s_id',None)
	f_id = request.GET.get('f_id',None)
	sub_id = request.GET.get('sub_id',None)
	
	question = Question.objects.filter(pk=q_id).first()
	student = Student.objects.filter(pk=s_id).first()
	faculty = Faculty.objects.filter(pk=f_id).first()
	subject = Subject.objects.filter(pk=sub_id).first()

	teacher_subject = TeacherSubject.objects.filter(classroom=student.classroom,teacher=faculty,subject=subject).first()
	
	try:
		fr = FeedbackResponse.objects.get(student=student,question=question,teacher_subject=teacher_subject)
		ansval = fr.answer
		print(ansval)
		return JsonResponse({
			'ans':ansval
		})
	except:
		return JsonResponse({
			'ans':0
		})		

@student_required
def feedback_faculty_theory(request):
	curr_user = request.user
	teachings = TeacherSubject.objects.filter(classroom=curr_user.student.classroom)
	courses = {teaching.subject:teaching.teacher for teaching in teachings}
	pass

@student_required
def feedback_infrastructure(request):
	#add form here and redirect to page
	pass

@student_required
def feedback_academics(request):
	#add form here and redirect to page
	pass

def signup(request):
	"""	if request.method == 'POST':
			form = SignUpForm(request.POST)
			if form.is_valid():
				user = form.save()
				user.refresh_from_db()  # load the profile instance created by the signal
				user.student.role = "student"
				user.student.student_name = form.cleaned_data.get('student_name')
				user.student.email = form.cleaned_data.get('email')
				user.student.phone_number = form.cleaned_data.get('phone_number')
				raw_password = form.cleaned_data.get('password1')
				user.student.save()
				user = authenticate(username=user.username, password=raw_password)
				login(request, user)
				return redirect('home')

		else:
			form = SignUpForm()
		return render(request, 'signup.html', {'form': form})
	"""
	pass

def login(request):
	if request.method == 'POST':
		form=LogInForm(request.POST)
		if form.is_valid():
			user=form
			username=form.cleaned_data['username']
			password=form.cleaned_data['password']
			user = authenticate(username=username, password=password)
			user_login(request, user)
			role=authenticate_role(user)

			if(role == 'STUDENT'):
				return redirect('student_dashboard')
			elif (role == 'FACULTY'):
				return redirect('faculty_dashboard')
			elif (role =='AUDITOR'):
				return redirect('auditor_profile')
			elif(role == 'COORDINATOR'):
				return redirect('coordinator_dashboard')


	else:
		form=LogInForm()
	return render(request, 'login_new.html', {'form': form})


def logout_view(request):
	logout(request)
	return redirect('login')

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            role=authenticate_role(user)

            if(role == 'STUDENT'):
                return redirect('student_dashboard')
            elif (role == 'FACULTY'):
                return redirect('faculty_dashboard')
            elif (role =='AUDITOR'):
                return redirect('auditor_profile')
            elif(role == 'COORDINATOR'):
                return redirect('coordinator_dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {
        'form': form
    })

import json
from django.db.models import Sum,Count
from django.core import serializers
def test_graph(request):
	"""academic_response =  FeedbackResponse.objects.filter(question__type__title="Academics").values('question').annotate(dsum=Sum('answer'),dcount = Count('student'))
				context = serializers.serialize('json', academic_response)
			"""
	return render(request, 'test_graph.html')