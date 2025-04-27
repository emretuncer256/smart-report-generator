from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib import messages
from django.conf import settings
import os
from .models import Report
from .utils import PDFReport
from datetime import datetime

# Create your views here.

def index(request):
    return render(request, 'report/index.html')

def handle_report_generation(request, report_type, template_name, generate_func):
    context = {}
    if request.method == 'POST':
        action = request.POST.get('action')
        options = {key: key in request.POST for key in request.POST.keys() if key.startswith('include_')}
        
        # PDF dosya adını oluştur
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'report_{timestamp}_{report_type}.pdf'
        
        try:
            # PDF oluştur
            pdf_report = PDFReport()
            generate_func(pdf_report, options)
            
            if action == 'preview':
                # Geçici dizini oluştur
                temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
                os.makedirs(temp_dir, exist_ok=True)
                temp_path = os.path.join(temp_dir, filename)
                
                # PDF'i geçici konuma kaydet
                pdf_report.output(temp_path, 'F')
                
                # PDF URL'ini context'e ekle
                context['pdf_url'] = f'/media/temp/{filename}'
                context['options'] = options
                return render(request, template_name, context)
                
            else:  # save
                # Kalıcı dizini oluştur
                permanent_dir = os.path.join(settings.MEDIA_ROOT, 'reports', report_type)
                os.makedirs(permanent_dir, exist_ok=True)
                permanent_path = os.path.join(permanent_dir, filename)
                
                # PDF'i kalıcı konuma kaydet
                pdf_report.output(permanent_path, 'F')
                
                # Raporu veritabanına kaydet
                report = Report(
                    title=f"{report_type.title()} Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    report_type=report_type,
                    file=f'reports/{report_type}/{filename}',
                    generated_by=request.user if request.user.is_authenticated else None
                )
                report.save()
                
                messages.success(request, 'Report generated and saved successfully!')
                return redirect('report:report_list')
                
        except Exception as e:
            messages.error(request, f'Error generating report: {str(e)}')
            # Hata durumunda geçici dosyayı temizle
            if action == 'preview' and 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
    
    return render(request, template_name, context)

def student_report(request):
    return handle_report_generation(
        request, 
        'student',
        'report/student_report.html',
        lambda pdf, options: pdf.generate_student_report(options)
    )

def course_report(request):
    return handle_report_generation(
        request, 
        'course',
        'report/course_report.html',
        lambda pdf, options: pdf.generate_course_report(options)
    )

def grade_report(request):
    return handle_report_generation(
        request, 
        'grade',
        'report/grade_report.html',
        lambda pdf, options: pdf.generate_grade_report(options)
    )

class ReportListView(ListView):
    model = Report
    template_name = 'report/report_list.html'
    context_object_name = 'reports'
    ordering = ['-created_at']
    paginate_by = 10

def delete_report(request, report_id):
    try:
        report = Report.objects.get(id=report_id)
        report.delete()
        messages.success(request, 'Report deleted successfully.')
    except Report.DoesNotExist:
        messages.error(request, 'Report not found.')
    except Exception as e:
        messages.error(request, f'Error deleting report: {str(e)}')
    
    return redirect('report:report_list')
