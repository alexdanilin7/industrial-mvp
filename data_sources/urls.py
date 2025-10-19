from django.urls import path
from . import views

urlpatterns = [
    path('excel-upload/', views.excel_upload_page, name='excel_upload_page'),
    path('generate-template/', views.generate_excel_template, name='generate_excel_template'),
    path('upload-file/', views.upload_excel_file, name='upload_excel_file'),
]