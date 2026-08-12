# M13_cross_modal_feature_standardization/models/models.py

from django.db import models


class StandardizedFeatureVector(models.Model):

    entity_id = models.CharField(
        max_length=255,
        db_index=True
    )

    feature_vector = models.JSONField()

    feature_vector_size = models.IntegerField()

    preprocessing_version = models.CharField(
        max_length=100
    )

    schema_version = models.CharField(
        max_length=100
    )

    missing_features = models.JSONField(
        default=list
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        db_table = (
            "m13_standardized_feature_vectors"
        )

        ordering = [
            "-created_at"
        ]

    def __str__(self):

        return (
            f"{self.entity_id} - "
            f"{self.preprocessing_version}"
        )