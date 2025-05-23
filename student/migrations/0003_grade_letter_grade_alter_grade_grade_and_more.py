# Generated by Django 5.1.7 on 2025-03-23 06:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0002_remove_course_semester'),
    ]

    operations = [
        migrations.AddField(
            model_name='grade',
            name='letter_grade',
            field=models.CharField(blank=True, choices=[('AA', 'AA (4.00) - Excellent'), ('BA', 'BA (3.50) - Very Good'), ('BB', 'BB (3.00) - Good'), ('CB', 'CB (2.50) - Fair'), ('CC', 'CC (2.00) - Pass'), ('FF', 'FF (0.00) - Fail')], max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='grade',
            name='grade',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='grade',
            name='grade_type',
            field=models.CharField(choices=[('P', 'Pass/Fail'), ('L', 'Letter Grade')], default='L', max_length=1),
        ),
        migrations.AlterUniqueTogether(
            name='grade',
            unique_together={('student', 'course')},
        ),
    ]
