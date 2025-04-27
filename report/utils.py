import os
import tempfile
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from io import BytesIO
from django.db.models import Count, Avg
from django.conf import settings
from student.models import Student, Course, Grade, Enrollment
import base64

class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_font('Arial', 'B', 16)
        self.gender_colors = {
            'F': '#FF69B4',
            'M': '#4169E1'
        }

    def get_gender_color(self, gender):
        if not gender:
            return '#808080'
        return self.gender_colors.get(gender, '#808080')

    def get_gender_label(self, gender):
        labels = {
            'F': 'Female',
            'M': 'Male'
        }
        return labels.get(gender, gender)

    def add_title(self, title):
        self.set_font('Arial', 'B', 24)
        self.cell(0, 10, title, ln=True, align='C')
        self.ln(10)
        self.set_font('Arial', size=12)

    def add_timestamp(self):
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', ln=True)
        self.ln(5)
        self.set_font('Arial', size=12)

    def add_chart(self, title):
        img_buffer = BytesIO()
        plt.title(title)
        plt.tight_layout()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=300)
        plt.close('all')
        
        img_buffer.seek(0)
        
        # Grafiği PDF'e ekle
        self.image(img_buffer, x=10, y=None, w=190)
        self.ln(10)
        
        # Buffer'ı kapat
        img_buffer.close()

    def generate_student_report(self, options):
        self.cell(0, 10, 'Student Report', 0, 1, 'C')
        self.ln(10)
        
        if options.get('include_total', False):
            total_students = Student.objects.count()
            self.set_font('Arial', '', 12)
            self.cell(0, 10, f'Total Students: {total_students}', 0, 1)
            self.ln(5)
        
        if options.get('include_gender', False):
            # Cinsiyet dağılımı grafiği
            plt.figure(figsize=(10, 6))
            gender_data = Student.objects.values('gender').annotate(count=Count('id'))
            
            # Verileri ve renkleri hazırla
            genders = [d['gender'] for d in gender_data]
            counts = [d['count'] for d in gender_data]
            colors = [self.get_gender_color(gender) for gender in genders]
            labels = [self.get_gender_label(gender) for gender in genders]
            
            # Grafik çiz
            plt.bar(labels, counts, color=colors)
            plt.title('Student Gender Distribution')
            plt.xlabel('Gender')
            plt.ylabel('Number of Students')
            self.add_chart('Gender Distribution')
        
        if options.get('include_performance', False):
            # Cinsiyet-performans grafiği
            plt.figure(figsize=(10, 6))
            # Öğrencilerin ortalama notlarını hesapla
            performance_data = Grade.objects.values('student__gender').annotate(avg_grade=Avg('grade'))
            
            # Verileri sırala ve renkleri hazırla
            genders = [d['student__gender'] for d in performance_data]
            grades = [d['avg_grade'] or 0 for d in performance_data]
            colors = [self.get_gender_color(gender) for gender in genders]
            labels = [self.get_gender_label(gender) for gender in genders]
            
            # Grafik çiz
            plt.bar(labels, grades, color=colors)
            plt.title('Student performance based on Gender')
            plt.xlabel('Gender')
            plt.ylabel('Average Grade')
            self.add_chart('Performance by Gender')

    def generate_course_report(self, options):
        self.cell(0, 10, 'Course Report', 0, 1, 'C')
        self.ln(10)
        
        if options.get('include_total', False):
            total_courses = Course.objects.count()
            self.set_font('Arial', '', 12)
            self.cell(0, 10, f'Total Courses: {total_courses}', 0, 1)
            self.ln(5)
        
        if options.get('include_enrollment', False):
            # Kayıt dağılımı grafiği
            plt.figure(figsize=(10, 6))
            enrollment_data = Course.objects.annotate(student_count=Count('enrollments'))
            plt.hist([c.student_count for c in enrollment_data], bins=20, color='#4169E1')
            plt.title('Course Enrollment Distribution')
            plt.xlabel('Number of Students')
            plt.ylabel('Number of Courses')
            self.add_chart('Enrollment Distribution')
        
        if options.get('include_performance', False):
            # Kurs performans grafiği
            plt.figure(figsize=(10, 6))
            course_data = Grade.objects.values('course__code').annotate(avg_grade=Avg('grade'))
            
            # Grafik çiz
            plt.bar(
                [d['course__code'] for d in course_data],
                [d['avg_grade'] or 0 for d in course_data],
                color='#4169E1'
            )
            plt.xticks(rotation=45)
            plt.title('Average Course Performance')
            plt.xlabel('Course Code')
            plt.ylabel('Average Grade')
            self.add_chart('Course Performance')

    def generate_grade_report(self, options):
        self.cell(0, 10, 'Grade Report', 0, 1, 'C')
        self.ln(10)
        
        if options.get('include_distribution', False):
            # Not dağılımı grafiği
            plt.figure(figsize=(10, 6))
            grade_data = Grade.objects.values('grade').annotate(count=Count('id'))
            plt.bar(
                [g['grade'] for g in grade_data], 
                [g['count'] for g in grade_data],
                color='#4169E1'
            )
            plt.title('Grade Distribution')
            plt.xlabel('Grade')
            plt.ylabel('Number of Students')
            self.add_chart('Grade Distribution')
        
        if options.get('include_gender_perf', False):
            # Cinsiyet-not dağılımı grafiği
            plt.figure(figsize=(10, 6))
            gender_data = Grade.objects.values('student__gender').annotate(avg_grade=Avg('grade'))
            
            # Verileri sırala ve renkleri hazırla
            genders = [g['student__gender'] for g in gender_data]
            grades = [g['avg_grade'] or 0 for g in gender_data]
            colors = [self.get_gender_color(gender) for gender in genders]
            labels = [self.get_gender_label(gender) for gender in genders]
            
            plt.bar(labels, grades, color=colors)
            plt.title('Average Grade by Gender')
            plt.xlabel('Gender')
            plt.ylabel('Average Grade')
            self.add_chart('Grade Distribution by Gender')

    def save(self):
        """PDF'i geçici dosyaya kaydeder"""
        temp_path = os.path.join(tempfile.gettempdir(), 'report.pdf')
        self.output(temp_path)
        return temp_path 