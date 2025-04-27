from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.db.models import Count, Avg
from .models import Student, Course, Grade, Enrollment
from .forms import StudentForm, CourseForm, GradeForm, EnrollmentForm

# Create your views here.

class DashboardView(TemplateView):
    template_name = 'student/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['total_students'] = Student.objects.count()
        context['total_courses'] = Course.objects.count()
        context['total_enrollments'] = Enrollment.objects.count()
        context['total_grades'] = Grade.objects.count()
        
        male_count = Student.objects.filter(gender='M').count()
        female_count = Student.objects.filter(gender='F').count()
        context['gender_distribution'] = {
            'male': male_count,
            'female': female_count
        }
        
        courses = Course.objects.annotate(student_count=Count('enrollments'))
        context['course_statistics'] = courses[:5]
        
        context['recent_enrollments'] = Enrollment.objects.select_related('student', 'course').order_by('-enrollment_date')[:5]
        context['recent_grades'] = Grade.objects.select_related('student', 'course').order_by('-date_recorded')[:5]
        
        return context

class StudentListView(ListView):
    model = Student
    template_name = 'student/student_list.html'
    context_object_name = 'students'
    paginate_by = 10

class StudentCreateView(CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'student/student_form.html'
    success_url = reverse_lazy('student:student_list')

class StudentUpdateView(UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'student/student_form.html'
    success_url = reverse_lazy('student:student_list')

class StudentDeleteView(DeleteView):
    model = Student
    template_name = 'student/student_confirm_delete.html'
    success_url = reverse_lazy('student:student_list')

class StudentDetailView(DetailView):
    model = Student
    template_name = 'student/student_detail.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        context['enrollments'] = student.enrollments.select_related('course').all()
        context['grades'] = student.grade_set.select_related('course').all()
        return context

class CourseListView(ListView):
    model = Course
    template_name = 'student/course_list.html'
    context_object_name = 'courses'

class CourseCreateView(CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'student/course_form.html'
    success_url = reverse_lazy('student:course_list')

class CourseUpdateView(UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'student/course_form.html'
    success_url = reverse_lazy('student:course_list')

class CourseDeleteView(DeleteView):
    model = Course
    template_name = 'student/course_confirm_delete.html'
    success_url = reverse_lazy('student:course_list')

class CourseDetailView(DetailView):
    model = Course
    template_name = 'student/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        context['enrollments'] = course.enrollments.select_related('student').all()
        context['grades'] = course.grade_set.select_related('student').all()
        context['average_grade'] = course.get_average_grade()
        context['student_count'] = course.get_student_count()
        return context

class GradeListView(ListView):
    model = Grade
    template_name = 'student/grade_list.html'
    context_object_name = 'grades'
    paginate_by = 10

    def get_queryset(self):
        return Grade.objects.select_related('student', 'course').all()

class GradeCreateView(CreateView):
    model = Grade
    form_class = GradeForm
    template_name = 'student/grade_form.html'
    success_url = reverse_lazy('student:grade_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        student_id = self.request.GET.get('student')
        course_id = self.request.GET.get('course')
        
        if student_id:
            try:
                student = Student.objects.get(pk=student_id)
                form.fields['student'].initial = student.id
            except Student.DoesNotExist:
                pass

        if course_id:
            try:
                course = Course.objects.get(pk=course_id)
                form.fields['course'].initial = course.id
            except Course.DoesNotExist:
                pass

        return form

    def form_valid(self, form):
        # Check if a grade already exists for this student and course
        student = form.cleaned_data['student']
        course = form.cleaned_data['course']
        existing_grade = Grade.objects.filter(student=student, course=course).exists()
        
        if existing_grade:
            form.add_error(None, 'A grade already exists for this student in this course.')
            return self.form_invalid(form)
            
        return super().form_valid(form)

class GradeUpdateView(UpdateView):
    model = Grade
    form_class = GradeForm
    template_name = 'student/grade_form.html'
    success_url = reverse_lazy('student:dashboard')

class GradeDeleteView(DeleteView):
    model = Grade
    template_name = 'student/grade_confirm_delete.html'
    success_url = reverse_lazy('student:dashboard')

class GradeDetailView(DetailView):
    model = Grade
    template_name = 'student/grade_detail.html'
    context_object_name = 'grade'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        grade = self.get_object()
        context['student'] = grade.student
        context['course'] = grade.course
        context['student_average'] = grade.student.get_average_grade(grade.course)
        context['course_average'] = grade.course.get_average_grade()
        return context

class EnrollmentListView(ListView):
    model = Enrollment
    template_name = 'student/enrollment_list.html'
    context_object_name = 'enrollments'
    paginate_by = 10

    def get_queryset(self):
        return Enrollment.objects.select_related('student', 'course').all()

class EnrollmentCreateView(CreateView):
    model = Enrollment
    form_class = EnrollmentForm
    template_name = 'student/enrollment_form.html'
    success_url = reverse_lazy('student:enrollment_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if 'student' in self.request.GET:
            student_id = self.request.GET.get('student')
            try:
                student = Student.objects.get(id=student_id)
                form.fields['student'].initial = student
                # Öğrencinin henüz kayıtlı olmadığı dersleri göster
                form.fields['course'].queryset = Course.objects.exclude(
                    enrollments__student=student
                ).distinct()
            except Student.DoesNotExist:
                pass
        return form

    def form_valid(self, form):
        # Aynı ders ve öğrenci için kayıt var mı kontrol et
        student = form.cleaned_data['student']
        course = form.cleaned_data['course']
        if Enrollment.objects.filter(student=student, course=course).exists():
            form.add_error(None, "Student is already enrolled in this course.")
            return self.form_invalid(form)
        return super().form_valid(form)

class EnrollmentUpdateView(UpdateView):
    model = Enrollment
    form_class = EnrollmentForm
    template_name = 'student/enrollment_form.html'
    success_url = reverse_lazy('student:enrollment_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        enrollment = self.get_object()
        form.fields['student'].initial = enrollment.student
        form.fields['course'].initial = enrollment.course
        return form

class EnrollmentDeleteView(DeleteView):
    model = Enrollment
    template_name = 'student/enrollment_confirm_delete.html'
    success_url = reverse_lazy('student:enrollment_list')

class EnrollmentDetailView(DetailView):
    model = Enrollment
    template_name = 'student/enrollment_detail.html'
    context_object_name = 'enrollment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enrollment = self.get_object()
        context['grades'] = enrollment.student.grade_set.filter(course=enrollment.course)
        context['average_grade'] = enrollment.student.get_average_grade(enrollment.course)
        return context
