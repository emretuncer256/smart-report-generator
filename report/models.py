from django.db import models
from django.contrib.auth.models import User
import os

class Report(models.Model):
    REPORT_TYPES = (
        ('student', 'Student Report'),
        ('course', 'Course Report'),
        ('grade', 'Grade Report'),
    )
    
    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    file = models.FileField(upload_to='reports/%Y/%m/%d/')
    created_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        if self.file:
            if os.path.isfile(self.file.path):
                try:
                    os.remove(self.file.path)
                except:
                    pass
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
