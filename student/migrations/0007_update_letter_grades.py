from django.db import migrations

def update_letter_grades(apps, schema_editor):
    Grade = apps.get_model('student', 'Grade')
    for grade in Grade.objects.all():
        if grade.grade_type != 'P':  # Project dışındaki tüm notlar için
            if 90 <= grade.grade <= 100:
                grade.letter_grade = 'AA'
            elif 80 <= grade.grade <= 89:
                grade.letter_grade = 'BA'
            elif 73 <= grade.grade <= 79:
                grade.letter_grade = 'BB'
            elif 66 <= grade.grade <= 72:
                grade.letter_grade = 'CB'
            elif 60 <= grade.grade <= 65:
                grade.letter_grade = 'CC'
            else:
                grade.letter_grade = 'FF'
        else:
            grade.letter_grade = None
        grade.save()

class Migration(migrations.Migration):
    dependencies = [
        ('student', '0006_alter_grade_grade_type'),
    ]

    operations = [
        migrations.RunPython(update_letter_grades),
    ] 