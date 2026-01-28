from django.db import models

class EquipmentDataset(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=255)
    summary = models.JSONField()
    # Optionally store the raw CSV as text or file
    # csv_file = models.FileField(upload_to='uploads/', null=True, blank=True)

    def __str__(self):
        return self.filename
