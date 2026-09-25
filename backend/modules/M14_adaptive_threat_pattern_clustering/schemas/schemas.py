"""
Schemas for Module 14.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class FeatureVector:
    """
    Represents one normalized feature vector.
    """

    entity_id: str
    features: List[float]


@dataclass
class BatchStatistics:
    """
    Statistics calculated for an incoming batch.
    """

    mean_dist: float
    cluster_dist: List[float]
    sample_count: int


@dataclass
class ClusterStatistics:
    """
    Statistics maintained for a cluster.
    """

    cluster_id: int
    size: int
    centroid: List[float]
    mean_distance: float
    distance_variance: float
    stability_score: float
    error_rate: float


@dataclass
class ProcessingResult:
    """
    Output returned by Module 14.
    """

    entity_id: str
    cluster_id: Optional[int]
    distance: Optional[float]
    centroid: Optional[List[float]]
    cluster_statistics: Optional[Dict[str, Any]]
    drift_detected: bool
    psi_score: float
    dist_zscore: float
    adwin_flagged: bool