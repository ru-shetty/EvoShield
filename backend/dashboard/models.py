from django.db import models


class ScanRecord(models.Model):
    entity_id = models.CharField(max_length=36, unique=True)
    source = models.CharField(max_length=32, default="web")
    entity_type = models.CharField(max_length=32)
    subject = models.CharField(max_length=500, blank=True)
    verdict = models.CharField(max_length=24)
    risk_score = models.FloatField(default=0)
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
