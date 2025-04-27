from django.urls import path
from . import views

app_name = 'report'

urlpatterns = [
    path('', views.index, name='index'),
    path('student/', views.student_report, name='student_report'),
    path('course/', views.course_report, name='course_report'),
    path('grade/', views.grade_report, name='grade_report'),
    path('list/', views.ReportListView.as_view(), name='report_list'),
    path('delete/<int:report_id>/', views.delete_report, name='delete_report'),
] 