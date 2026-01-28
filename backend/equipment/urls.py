from django.urls import path
from .views import EquipmentUploadView, EquipmentHistoryView, EquipmentPDFReportView
from rest_framework import generics
from .models import EquipmentDataset
from .views import EquipmentDatasetSerializer

urlpatterns = [
    path('upload/', EquipmentUploadView.as_view(), name='equipment-upload'),
    path('history/', EquipmentHistoryView.as_view(), name='equipment-history'),
    path('report/<int:pk>/', EquipmentPDFReportView.as_view(), name='equipment-pdf-report'),
]
