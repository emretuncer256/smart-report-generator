# Generated by Django 5.1.7 on 2025-05-10 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0005_alter_grade_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grade',
            name='grade_type',
            field=models.CharField(choices=[('M', 'Midterm'), ('F', 'Final'), ('P', 'Project')], default='M', max_length=1),
        ),
    ]
