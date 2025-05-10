from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, FormView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.db.models import Count, Avg
from .models import Student, Course, Grade, Enrollment
from .forms import StudentForm, CourseForm, GradeForm, EnrollmentForm, BulkEnrollmentForm
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from django.utils import timezone
from django.views import View

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

    def get_queryset(self):
        return Student.objects.filter(is_active=True)

class InactiveStudentListView(ListView):
    model = Student
    template_name = 'student/inactive_student_list.html'
    context_object_name = 'students'
    paginate_by = 10

    def get_queryset(self):
        return Student.objects.filter(is_active=False)

def activate_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.is_active = True
    student.save()
    messages.success(request, f'Student {student.first_name} {student.last_name} has been activated successfully.')
    return redirect('student:inactive_student_list')

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

    def post(self, request, *args, **kwargs):
        student = self.get_object()
        student.is_active = False
        student.save()
        messages.success(request, f'Student {student.first_name} {student.last_name} has been deactivated successfully.')
        return redirect(self.success_url)

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

        # Sadece aktif öğrencileri göster
        form.fields['student'].queryset = Student.objects.filter(is_active=True)
        return form

    def form_valid(self, form):
        # Öğrencinin aktif olup olmadığını kontrol et
        student = form.cleaned_data['student']
        if not student.is_active:
            form.add_error('student', 'Cannot add grade for an inactive student.')
            return self.form_invalid(form)

        # Check if a grade already exists for this student and course
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
        student_id = self.request.GET.get('student')
        
        if student_id:
            try:
                student = Student.objects.get(id=student_id)
                form.fields['student'].initial = student
                
                # Get available courses for the student
                available_courses = Course.objects.exclude(
                    enrollments__student=student
                ).distinct()
                
                if not available_courses.exists():
                    messages.warning(self.request, f'No courses available for {student.get_full_name()}.')
                
                form.fields['courses'].queryset = available_courses
            except Student.DoesNotExist:
                messages.error(self.request, 'Selected student does not exist.')
        
        return form

    def form_valid(self, form):
        student = form.cleaned_data['student']
        
        if not student.is_active:
            messages.error(self.request, f'Cannot enroll inactive student: {student.get_full_name()}')
            return self.form_invalid(form)
        
        enrollments = form.save()
        
        if enrollments:
            messages.success(
                self.request,
                f'Successfully enrolled {student.get_full_name()} in {len(enrollments)} course(s).'
            )
            return redirect(self.success_url)
        else:
            messages.warning(self.request, 'No courses were selected for enrollment.')
            return self.form_invalid(form)

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

class BulkEnrollmentView(FormView):
    form_class = BulkEnrollmentForm
    template_name = 'student/bulk_enrollment.html'
    success_url = reverse_lazy('student:enrollment_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if 'student' in self.request.GET:
            student_id = self.request.GET.get('student')
            try:
                student = Student.objects.get(id=student_id)
                form.fields['student'].initial = student
                form.fields['courses'].queryset = Course.objects.exclude(
                    enrollments__student=student
                ).distinct()
            except Student.DoesNotExist:
                pass
        return form

    def form_valid(self, form):
        student = form.cleaned_data['student']
        courses = form.cleaned_data['courses']
        semester = form.cleaned_data['semester']

        # Öğrencinin aktif olup olmadığını kontrol et
        if not student.is_active:
            form.add_error('student', 'Cannot enroll an inactive student.')
            return self.form_invalid(form)

        success_count = 0
        error_count = 0

        for course in courses:
            # Aynı ders ve öğrenci için kayıt var mı kontrol et
            if not Enrollment.objects.filter(student=student, course=course, semester=semester).exists():
                try:
                    Enrollment.objects.create(
                        student=student,
                        course=course,
                        semester=semester
                    )
                    success_count += 1
                except Exception as e:
                    error_count += 1
            else:
                error_count += 1

        if success_count > 0:
            messages.success(
                self.request,
                f'Successfully enrolled student in {success_count} course(s).'
            )
        if error_count > 0:
            messages.warning(
                self.request,
                f'Could not enroll student in {error_count} course(s) (already enrolled or error occurred).'
            )

        return super().form_valid(form)

def get_available_courses(request):
    student_id = request.GET.get('student')
    if not student_id:
        return JsonResponse({'courses': []})

    try:
        student = Student.objects.get(id=student_id)
        available_courses = Course.objects.exclude(
            enrollments__student=student
        ).distinct().values('id', 'name')

        return JsonResponse({
            'courses': list(available_courses)
        })
    except Student.DoesNotExist:
        return JsonResponse({'courses': []})

class CourseEnrollmentView(FormView):
    template_name = 'student/course_enrollment_form.html'
    form_class = EnrollmentForm
    success_url = reverse_lazy('student:enrollment_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['course_id'] = self.kwargs.get('course_id')
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs.get('course_id')
        
        try:
            course = Course.objects.get(id=course_id)
            context['course'] = course
        except Course.DoesNotExist:
            messages.error(self.request, 'Course not found.')
            return redirect('student:enrollment_list')
            
        return context

    def form_valid(self, form):
        course = form.cleaned_data['course']
        semester = form.cleaned_data['semester']
        selected_students = form.cleaned_data['students']

        if not selected_students:
            messages.warning(self.request, 'Please select at least one student.')
            return self.form_invalid(form)

        success_count = 0
        error_count = 0

        for student in selected_students:
            try:
                # Check if student is already enrolled
                if Enrollment.objects.filter(
                    student=student,
                    course=course,
                    semester=semester
                ).exists():
                    messages.warning(
                        self.request,
                        f'Student {student} is already enrolled in this course for {semester}.'
                    )
                    error_count += 1
                    continue

                # Create enrollment
                Enrollment.objects.create(
                    student=student,
                    course=course,
                    semester=semester
                )
                success_count += 1

            except Exception as e:
                messages.error(
                    self.request,
                    f'Error enrolling {student}: {str(e)}'
                )
                error_count += 1

        if success_count > 0:
            messages.success(
                self.request,
                f'Successfully enrolled {success_count} student(s) in {course.name}.'
            )
            return super().form_valid(form)
        else:
            messages.error(
                self.request,
                f'Failed to enroll any students. {error_count} error(s) occurred.'
            )
            return self.form_invalid(form)

class BulkGradeEntryView(View):
    template_name = 'student/bulk_grade_entry.html'

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        enrollments = Enrollment.objects.filter(course=course)
        
        # Get all grade types for the form
        grade_types = Grade.GRADE_TYPE_CHOICES
        
        context = {
            'course': course,
            'enrollments': enrollments,
            'grade_types': grade_types,
        }
        return render(request, self.template_name, context)

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        enrollments = Enrollment.objects.filter(course=course)
        
        success_count = 0
        error_count = 0
        
        for enrollment in enrollments:
            student_id = str(enrollment.student.id)
            grade_value = request.POST.get(f'grade_{student_id}')
            grade_type = request.POST.get(f'type_{student_id}')
            
            if grade_value and grade_type:
                try:
                    # Check if grade already exists for this student and course
                    existing_grade = Grade.objects.filter(
                        student=enrollment.student,
                        course=course,
                        grade_type=grade_type
                    ).first()
                    
                    if existing_grade:
                        # Update existing grade
                        existing_grade.grade = grade_value
                        existing_grade.save()
                    else:
                        # Create new grade
                        Grade.objects.create(
                            student=enrollment.student,
                            course=course,
                            grade=grade_value,
                            grade_type=grade_type,
                            date_recorded=timezone.now()
                        )
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    messages.error(request, f"Error adding grade for {enrollment.student.get_full_name()}: {str(e)}")
        
        if success_count > 0:
            messages.success(request, f"Successfully added/updated grades for {success_count} students.")
        if error_count > 0:
            messages.warning(request, f"Failed to add/update grades for {error_count} students.")
            
        return redirect('student:course_detail', pk=course.id)
