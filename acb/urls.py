from django.urls import path
from .import views

urlpatterns=[
    path('',views.index,name='index'),
    path('index/',views.index,name='index'),
    path('studentindex/',views.studentindex,name='studenindex'),
    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('profile/',views.profile,name='profile'),
    path('edit_profile/<int:uid>/',views.edit_profile,name='edit_profile'),
    path('logout/',views.logout,name='logout'),
    path('feedback_rate/',views.feedback,name='feedback_rate'),

    path('teacherindex/',views.teacherindex,name='teacherindex'),
    path('teacherreg/',views.teacherreg,name='teacherreg'),
    path('teacherlogin/',views.teacherlogin,name='teacherlogin'),
    path('teacherprofile/',views.teacherprofile,name='teacherprofile'),
    path('T_edit_profile/<int:id>/',views.T_edit_profile, name='T_edit_profile'),

    # admin details ....
    path('adminhome/',views.adminhome,name='adminhome'),
    path('studentlist/',views.admin_studentlist,name='studentlist'),
    path('student_delete/<int:sid>/',views.student_delete,name='student_delete'),
    path('teacherlist/',views.admin_teacherlist,name='teacherlist'),
    path('teacher_delete/<int:sid>/',views.teacher_delete,name='teacher_delete'),
    path('update_status/',views.update_status,name='update_status'),
    path('feedbacklist/',views.admin_feedbacklist,name='feedbacklist'),
    path('feedback_delete/<int:fid>/',views.feedback_delete,name='feedback_delete'),

    #admin login .....
    path('adminlogin/',views.admin_login,name='adminlogin'),
    path('ai/',views.codeexplainer,name='ai'),
    path('math/',views.mathexplainer,name='math'),



# Student URLs
    path('attendence/', views.view_attendance, name='view_attendance'),
    path('upload-assignment/', views.upload_assignment, name='upload_assignment'),
    path('results/', views.view_results, name='view_results'),
    path('notes/', views.view_notes, name='view_notes'),

    # Teacher URLs
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('add-result/', views.add_result, name='add_result'),
    path('upload/', views.upload_notes, name='upload'),
    path('assignments/', views.assignment_v, name='view_assignment'),

]   

