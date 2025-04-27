from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'created_at', 'generated_by', 'file_size')
    list_filter = ('report_type', 'created_at', 'generated_by')
    search_fields = ('title', 'description', 'generated_by')
    readonly_fields = ('created_at', 'file_size')
    ordering = ('-created_at',)

    def file_size(self, obj):
        """Dosya boyutunu formatlar"""
        size = obj.file_size
        if size < 1024:
            return f"{size} bytes"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} KB"
        else:
            return f"{size/(1024*1024):.1f} MB"
    file_size.short_description = 'File Size'
