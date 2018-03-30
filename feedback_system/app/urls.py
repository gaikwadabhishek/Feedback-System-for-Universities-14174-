from django.urls import path, include
from app import views
from django.contrib.auth import views as auth_views

urlpatterns = [
	path('home/', views.home,name = 'home'),
	path('signup/', views.signup, name='signup'),
	path('', views.login, name='login'),
	path('logout_view/', views.logout_view, name='logout_view'),
	path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
	path('student_dashboard/ajax', views.ajax_student_dashboard, name='ajax_student_dashboard'),
	path('student_profile/', views.student_profile, name='student_profile'),
	path('faculty_dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
	path('faculty_profile/', views.faculty_profile, name='faculty_profile'),
	path('auditor_profile/', views.auditor_profile, name='auditor_profile'),
	path('auditor_dashboard/', views.auditor_dashboard, name='auditor_dashboard'),
	path('coordinator_profile/', views.coordinator_profile, name='coordinator_profile'),
	path('coordinator_dashboard/', views.coordinator_dashboard, name='coordinator_dashboard'),
	path('publish_form/<int:formid>', views.publish_form, name='publish_form'),
	path('activate_form/<int:formid>', views.activate_form, name='activate_form'),
	path('deactivate_form/<int:formid>', views.deactivate_form, name='deactivate_form'),
	path('edit_form/ajax/title', views.edit_form_title, name='edit_form_title'),
	path('edit_form/ajax/delq', views.ajax_delete_question, name='ajax_delete_question'),	
	path('edit_form/ajax/question', views.edit_form_question, name='edit_form_question'),	
	path('edit_form/<int:formid>/ajax/title', views.edit_form_title, name='edit_form_title'),
	path('edit_form/<int:formid>/ajax/delq', views.ajax_delete_question, name='ajax_delete_question'),
	path('edit_form/<int:formid>/ajax/question', views.ajax_add_questions, name='edit_form_question'),	
	path('edit_form/', views.edit_form, name='edit_form'),	
	path('edit_form/<int:formid>', views.edit_form, name='edit_form'),	
	path('copy_form/<int:formid>', views.copy_form, name='copy_form'),	
	path('create_form/', views.create_form, name='create_form'),
	path('add_questions/ajax', views.ajax_add_questions, name='ajax_add_questions'),
	path('add_questions/<int:formid>', views.add_questions, name='add_questions'),
	path('student_feedback/<int:formid>', views.student_feedback, name='student_feedback'),
	path('student_feedback/ajax/textual', views.ajax_text_response, name='ajax_text_response'),

	path('edit_form/<int:formid>/ajax/predict_tags', views.ajax_predict_tags, name='ajax_predict_tags'),

	path('edit_form/ajax/predict_tags', views.ajax_predict_tags, name='ajax_predict_tags'),


	path('student_feedback/<int:formid>/ajax/textual', views.ajax_text_response, name='ajax_text_response'),
	path('feedback_faculty/<int:formid>', views.feedback_faculty, name='feedback_faculty'),
	path('ajax/student_feedback_response_set', views.student_feedback_response_set, name='student_feedback_response_set'),
	path('ajax/student_feedback_response_get', views.student_feedback_response_get,
	name='student_feedback_response_get'),
	path('ajax/student_feedback_faculty_response_get', views.student_feedback_faculty_response_get,
	name='student_feedback_faculty_response_get'),
	path('ajax/student_feedback_faculty_response_set', views.student_feedback_faculty_response_set,
	name='student_feedback_faculty_response_set'),
	#give faculty feedback for theory lectures(rating based)
	path('student_profile/feedback_faculty_theory', views.feedback_faculty_theory, name='feedback_faculty_theory'),
	path('student_profile/feedback_infrastructure', views.feedback_infrastructure, name='feedback_infrastructure'),
	path('student_profile/feedback_academics', views.feedback_academics, name='feedback_academics'),
	path('events/', views.events, name='events'),
	path('change_password/', views.change_password, name='change_password'),
	path('test_graph/', views.test_graph, name='test_graph'),
]
