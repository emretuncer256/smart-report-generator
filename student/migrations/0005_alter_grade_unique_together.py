# Generated by Django 5.1.7 on 2025-05-10 17:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0004_student_is_active_alter_grade_grade_type'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='grade',
            unique_together={('student', 'course', 'grade_type')},
        ),
    ]
