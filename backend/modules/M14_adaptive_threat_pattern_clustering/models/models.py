"""
Database models for Module 14.
"""

from django.db import models


class ClusterRecord(models.Model):
    """
    Stores the current statistics of each cluster.
    """

    cluster_id = models.IntegerField(unique=True)

    size = models.PositiveIntegerField(default=0)

    centroid = models.JSONField(default=list)

    mean_distance = models.FloatField(default=0.0)

    distance_variance = models.FloatField(default=0.0)

    stability_score = models.FloatField(default=0.0)

    error_rate = models.FloatField(default=0.0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "m14_cluster_record"

    def __str__(self):
        return f"Cluster {self.cluster_id}"


class ClusterAssignment(models.Model):
    """
    Stores the cluster assigned to each processed entity.
    """

    entity_id = models.CharField(max_length=255)

    cluster_id = models.IntegerField()

    distance = models.FloatField(default=0.0)

    feature_vector = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "m14_cluster_assignment"
        indexes = [
            models.Index(fields=["entity_id"]),
            models.Index(fields=["cluster_id"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return (
            f"{self.entity_id} -> Cluster {self.cluster_id}"
        )