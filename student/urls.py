from django.urls import path
from . import views

app_name = 'student'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Student URLs
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('students/inactive/', views.InactiveStudentListView.as_view(), name='inactive_student_list'),
    path('students/add/', views.StudentCreateView.as_view(), name='student_add'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('students/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student_edit'),
    path('students/<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student_delete'),
    path('students/<int:pk>/activate/', views.activate_student, name='activate_student'),
    
    # Course URLs
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/add/', views.CourseCreateView.as_view(), name='course_add'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('courses/<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course_edit'),
    path('courses/<int:pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),
    path('courses/<int:course_id>/bulk-grades/', views.BulkGradeEntryView.as_view(), name='course_bulk_grades'),
    
    # Enrollment URLs
    path('enrollments/', views.EnrollmentListView.as_view(), name='enrollment_list'),
    path('enrollments/add/', views.EnrollmentCreateView.as_view(), name='enrollment_add'),
    path('enrollments/course/<int:course_id>/add/', views.CourseEnrollmentView.as_view(), name='course_enrollment_add'),
    path('enrollments/bulk/', views.BulkEnrollmentView.as_view(), name='bulk_enrollment'),
    path('enrollments/<int:pk>/', views.EnrollmentDetailView.as_view(), name='enrollment_detail'),
    path('enrollments/<int:pk>/edit/', views.EnrollmentUpdateView.as_view(), name='enrollment_edit'),
    path('enrollments/<int:pk>/delete/', views.EnrollmentDeleteView.as_view(), name='enrollment_delete'),
    path('enrollments/get-available-courses/', views.get_available_courses, name='get_available_courses'),
    
    # Grade URLs
    path('grades/', views.GradeListView.as_view(), name='grade_list'),
    path('grades/add/', views.GradeCreateView.as_view(), name='grade_add'),
    path('grades/<int:pk>/', views.GradeDetailView.as_view(), name='grade_detail'),
    path('grades/<int:pk>/edit/', views.GradeUpdateView.as_view(), name='grade_edit'),
    path('grades/<int:pk>/delete/', views.GradeDeleteView.as_view(), name='grade_delete'),
] 