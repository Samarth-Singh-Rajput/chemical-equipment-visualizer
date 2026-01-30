from django.shortcuts import render
from rest_framework import serializers, status, views
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from django.http import HttpResponse
from .models import EquipmentDataset
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd
import os
import io
from django.core.files.storage import default_storage

class EquipmentDatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentDataset
        fields = ['id', 'uploaded_at', 'filename', 'summary']

class EquipmentUploadView(views.APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        # Save file temporarily
        file_path = default_storage.save(file_obj.name, file_obj)
        abs_path = default_storage.path(file_path)
        # Read CSV with pandas
        try:
            df = pd.read_csv(abs_path)
        except Exception as e:
            return Response({'error': f'Invalid CSV: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        # Calculate summary
        summary = {
            'total_count': len(df),
            'averages': df.select_dtypes(include='number').mean().to_dict(),
            'type_distribution': df['Type'].value_counts().to_dict() if 'Type' in df.columns else {},
        }
        # Save to DB
        dataset = EquipmentDataset.objects.create(
            filename=file_obj.name,
            summary=summary
        )
        # Keep only last 5 datasets: if more than 5, delete the oldest
        if EquipmentDataset.objects.count() > 5:
            oldest = EquipmentDataset.objects.order_by('uploaded_at').first()
            oldest.delete()
        # Remove temp file
        os.remove(abs_path)
        return Response(EquipmentDatasetSerializer(dataset).data, status=status.HTTP_201_CREATED)

class EquipmentHistoryView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        datasets = EquipmentDataset.objects.order_by('-uploaded_at')[:5]
        serializer = EquipmentDatasetSerializer(datasets, many=True)
        return Response(serializer.data)

class EquipmentPDFReportView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            dataset = EquipmentDataset.objects.get(pk=pk)
        except EquipmentDataset.DoesNotExist:
            return Response({'error': 'Dataset not found'}, status=404)
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica", 14)
        p.drawString(100, 750, f"Equipment Dataset Report: {dataset.filename}")
        p.setFont("Helvetica", 12)
        y = 720
        summary = dataset.summary
        p.drawString(100, y, f"Total Count: {summary.get('total_count', '-')}")
        y -= 20
        p.drawString(100, y, "Averages:")
        for k, v in summary.get('averages', {}).items():
            y -= 20
            p.drawString(120, y, f"{k}: {v}")
        y -= 20
        p.drawString(100, y, "Type Distribution:")
        for k, v in summary.get('type_distribution', {}).items():
            y -= 20
            p.drawString(120, y, f"{k}: {v}")
        p.showPage()
        p.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{dataset.filename}_report.pdf"'
        return response
# Create your views here.
