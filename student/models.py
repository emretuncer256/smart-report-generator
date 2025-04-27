from django.db import models
from django.db.models import Avg, Count, Q, Max, Min
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=(('M', 'Male'), ('F', 'Female')))
    picture = models.ImageField(upload_to='student/pictures', blank=True, default='student/default.png')
    birth_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    student_id = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_course_grades(self, course):
        return self.grade_set.filter(course=course)

    def get_average_grade(self, course):
        grades = self.get_course_grades(course)
        return grades.aggregate(Avg('grade'))['grade__avg'] or 0

    def is_passing(self, course, passing_grade=60):
        return self.get_average_grade(course) >= passing_grade

    def get_all_courses(self):
        return Course.objects.filter(enrollments__student=self).distinct()

    def get_failing_courses(self, passing_grade=60):
        return [course for course in self.get_all_courses() 
                if not self.is_passing(course, passing_grade)]

    @classmethod
    def get_gender_distribution(cls, course):
        total = cls.objects.filter(enrollments__course=course).count()
        if total == 0:
            return {'M': 0, 'F': 0}
        
        male_count = cls.objects.filter(
            enrollments__course=course,
            gender='M'
        ).count()
        female_count = total - male_count
        
        return {
            'M': (male_count / total) * 100,
            'F': (female_count / total) * 100
        }

    @classmethod
    def get_pass_fail_distribution(cls, course, passing_grade=60):
        students = cls.objects.filter(enrollments__course=course)
        total = students.count()
        if total == 0:
            return {'pass': 0, 'fail': 0}
        
        passing = sum(1 for student in students if student.is_passing(course, passing_grade))
        failing = total - passing
        
        return {
            'pass': (passing / total) * 100,
            'fail': (failing / total) * 100
        }


class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)
    credits = models.IntegerField(default=3)
    instructor = models.CharField(max_length=100, blank=True)
    year = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_all_students(self):
        return Student.objects.filter(enrollments__course=self).distinct()

    def get_student_count(self):
        return self.get_all_students().count()

    def get_average_grade(self):
        grades = self.grade_set.all()
        return grades.aggregate(Avg('grade'))['grade__avg'] or 0

    def get_passing_students(self, passing_grade=60):
        return [student for student in self.get_all_students() 
                if student.is_passing(self, passing_grade)]

    def get_failing_students(self, passing_grade=60):
        return [student for student in self.get_all_students() 
                if not student.is_passing(self, passing_grade)]

    def get_makeup_list(self, grade_threshold=35):
        return self.get_failing_students().filter(
            grade__grade__lt=grade_threshold
        )

    def get_grade_distribution(self):
        grades = self.grade_set.all()
        distribution = {
            'A': grades.filter(grade__gte=90).count(),
            'B': grades.filter(grade__gte=80, grade__lt=90).count(),
            'C': grades.filter(grade__gte=70, grade__lt=80).count(),
            'D': grades.filter(grade__gte=60, grade__lt=70).count(),
            'F': grades.filter(grade__lt=60).count()
        }
        return distribution


class Enrollment(models.Model):
    SEMESTER_CHOICES = [
        ('FALL', 'Fall Semester'),
        ('SPRING', 'Spring Semester'),
        ('SUMMER', 'Summer Semester')
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES, default='FALL')
    enrollment_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'course', 'semester']
        ordering = ['-enrollment_date']

    def __str__(self):
        return f"{self.student} - {self.course} ({self.get_semester_display()})"


class Grade(models.Model):
    GRADE_TYPE_CHOICES = [
        ('M', 'Midterm'),
        ('F', 'Final'),
        ('P', 'Project'),
    ]

    LETTER_GRADE_CHOICES = [
        ('AA', 'AA (4.00) - Excellent'),
        ('BA', 'BA (3.50) - Very Good'),
        ('BB', 'BB (3.00) - Good'),
        ('CB', 'CB (2.50) - Fair'),
        ('CC', 'CC (2.00) - Pass'),
        ('FF', 'FF (0.00) - Fail'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    grade = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    grade_type = models.CharField(max_length=1, choices=GRADE_TYPE_CHOICES, default='L')
    letter_grade = models.CharField(max_length=2, choices=LETTER_GRADE_CHOICES, null=True, blank=True)
    is_makeup = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    date_recorded = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'course']

    def __str__(self):
        if self.grade_type == 'P':
            return f"{self.student} - {self.course} - {'Pass' if self.grade >= 60 else 'Fail'}"
        return f"{self.student} - {self.course} - {self.letter_grade}"

    def get_numerical_grade(self):
        if self.grade_type == 'P':
            return 4.0 if self.grade >= 60 else 0.0
        
        grade_mapping = {
            'AA': 4.00,
            'BA': 3.50,
            'BB': 3.00,
            'CB': 2.50,
            'CC': 2.00,
            'FF': 0.00
        }
        return grade_mapping.get(self.letter_grade, 0.0)

    def save(self, *args, **kwargs):
        if self.grade_type == 'L':
            if 90 <= self.grade <= 100:
                self.letter_grade = 'AA'
            elif 80 <= self.grade <= 89:
                self.letter_grade = 'BA'
            elif 73 <= self.grade <= 79:
                self.letter_grade = 'BB'
            elif 66 <= self.grade <= 72:
                self.letter_grade = 'CB'
            elif 60 <= self.grade <= 65:
                self.letter_grade = 'CC'
            else:
                self.letter_grade = 'FF'
        else:
            self.letter_grade = None
        super().save(*args, **kwargs)

    def get_letter_grade(self):
        if self.grade >= 90:
            return 'A'
        elif self.grade >= 80:
            return 'B'
        elif self.grade >= 70:
            return 'C'
        elif self.grade >= 60:
            return 'D'
        else:
            return 'F'

    def is_passing(self, passing_grade=60):
        return self.grade >= passing_grade

    @classmethod
    def get_course_statistics(cls, course):
        grades = cls.objects.filter(course=course)
        return {
            'average': grades.aggregate(Avg('grade'))['grade__avg'] or 0,
            'highest': grades.aggregate(Max('grade'))['grade__max'] or 0,
            'lowest': grades.aggregate(Min('grade'))['grade__min'] or 0,
            'count': grades.count(),
            'passing': grades.filter(grade__gte=60).count(),
            'failing': grades.filter(grade__lt=60).count()
        }
