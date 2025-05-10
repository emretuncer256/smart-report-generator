from django import forms
from .models import Student, Course, Grade, Enrollment
from django.utils import timezone

class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, (forms.Select, forms.NumberInput, forms.TextInput, forms.EmailInput)):
                field.widget.attrs.update({
                    'class': 'form-select' if isinstance(field.widget, forms.Select) else 'form-control',
                    'style': 'height: 45px;'
                })
            elif not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})

class StudentForm(BaseForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'gender', 'picture', 'birth_date', 
                 'student_id', 'email', 'phone', 'address']
        widgets = {
            'birth_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'style': 'height: 45px;'
            }),
            'address': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control'
            }),
            'gender': forms.RadioSelect(attrs={
                'class': 'form-check-input me-2'
            }),
            'picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

class CourseForm(BaseForm):
    class Meta:
        model = Course
        fields = ['name', 'code', 'description', 'credits', 'instructor', 'year']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control'
            }),
            'credits': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'style': 'height: 45px;'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2000,
                'style': 'height: 45px;'
            }),
        }

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['student', 'course', 'grade', 'grade_type', 'letter_grade', 'is_makeup', 'notes']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select select2'}),
            'course': forms.Select(attrs={'class': 'form-select select2'}),
            'grade': forms.NumberInput(attrs={'class': 'form-control grade-input', 'min': '0', 'max': '100', 'step': '0.01'}),
            'grade_type': forms.Select(attrs={'class': 'form-select'}),
            'letter_grade': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['letter_grade'].required = False
        self.fields['letter_grade'].widget.attrs['disabled'] = True

    def clean(self):
        cleaned_data = super().clean()
        grade = cleaned_data.get('grade')
        grade_type = cleaned_data.get('grade_type')

        if grade is not None:
            if grade < 0 or grade > 100:
                raise forms.ValidationError('Grade must be between 0 and 100.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.grade is not None:
            if 90 <= instance.grade <= 100:
                instance.letter_grade = 'AA'
            elif 80 <= instance.grade <= 89:
                instance.letter_grade = 'BA'
            elif 73 <= instance.grade <= 79:
                instance.letter_grade = 'BB'
            elif 66 <= instance.grade <= 72:
                instance.letter_grade = 'CB'
            elif 60 <= instance.grade <= 65:
                instance.letter_grade = 'CC'
            else:
                instance.letter_grade = 'FF'
        if commit:
            instance.save()
        return instance

class EnrollmentForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=forms.HiddenInput(),
        required=True
    )
    semester = forms.ChoiceField(
        choices=Enrollment.SEMESTER_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True,
        label='Select Students'
    )

    def __init__(self, *args, **kwargs):
        course_id = kwargs.pop('course_id', None)
        super().__init__(*args, **kwargs)
        
        if course_id:
            try:
                course = Course.objects.get(id=course_id)
                self.fields['course'].initial = course
                
                # Get active students not enrolled in this course
                enrolled_students = Enrollment.objects.filter(
                    course=course
                ).values_list('student_id', flat=True)
                
                available_students = Student.objects.filter(
                    is_active=True
                ).exclude(id__in=enrolled_students)
                
                self.fields['students'].queryset = available_students
                
            except Course.DoesNotExist:
                pass

    def get_student_list(self):
        """Return list of students for template display"""
        return self.fields['students'].queryset

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        courses = cleaned_data.get('courses')
        semester = cleaned_data.get('semester')

        if student and courses and semester:
            # Öğrencinin seçilen dönemde zaten kayıtlı olduğu dersleri bul
            existing_enrollments = Enrollment.objects.filter(
                student=student,
                semester=semester,
                course__in=courses
            ).values_list('course__name', flat=True)

            if existing_enrollments:
                # Eğer varsa, bu dersleri courses listesinden çıkar
                courses_to_remove = Course.objects.filter(name__in=existing_enrollments)
                cleaned_data['courses'] = courses.exclude(id__in=courses_to_remove)
                
                # Kullanıcıya bilgi ver
                if len(existing_enrollments) == 1:
                    raise forms.ValidationError(
                        f'Student is already enrolled in {existing_enrollments[0]} for the selected semester.'
                    )
                else:
                    raise forms.ValidationError(
                        f'Student is already enrolled in the following courses for the selected semester: {", ".join(existing_enrollments)}'
                    )

        return cleaned_data

    def save(self, commit=True):
        enrollments = []
        student = self.cleaned_data['student']
        courses = self.cleaned_data['courses']
        semester = self.cleaned_data['semester']
        enrollment_date = self.cleaned_data['enrollment_date']

        for course in courses:
            # Son bir kontrol daha yap
            if not Enrollment.objects.filter(student=student, course=course, semester=semester).exists():
                enrollment = Enrollment(
                    student=student,
                    course=course,
                    semester=semester,
                    enrollment_date=enrollment_date
                )
                if commit:
                    enrollment.save()
                enrollments.append(enrollment)

        return enrollments


class BulkEnrollmentForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=Student.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True
    )
    semester = forms.ChoiceField(
        choices=Enrollment.SEMESTER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    ) 