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

class EnrollmentForm(BaseForm):
    enrollment_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'style': 'height: 45px;'
        }),
        initial=timezone.now
    )

    class Meta:
        model = Enrollment
        fields = ['student', 'course', 'semester', 'enrollment_date']
        widgets = {
            'student': forms.Select(attrs={
                'class': 'form-select',
                'style': 'height: 45px;'
            }),
            'course': forms.Select(attrs={
                'class': 'form-select',
                'style': 'height: 45px;'
            }),
            'semester': forms.Select(attrs={
                'class': 'form-select',
                'style': 'height: 45px;'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        course = cleaned_data.get('course')
        semester = cleaned_data.get('semester')

        if student and course and semester:
            if Enrollment.objects.filter(student=student, course=course, semester=semester).exists():
                raise forms.ValidationError('Student is already enrolled in this course for the selected semester.')

        return cleaned_data 