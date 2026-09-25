"""
Module 14 — Adaptive Threat Pattern Clustering

Algorithm:

INITIALIZE:
    model = MiniBatchKMeans(...)
    baseline_stats = None
    baseline_var = None
    alpha = 0.1
    k_sigma = 3
    window = AdaptiveWindow()

FOR each incoming batch B:

    X <- preprocess(B)

    model.partial_fit(X)

    labels <- model.predict(X)

    dists <- distance_to_assigned_centroid(...)

    batch_stats <- {
        mean_dist,
        cluster_dist
    }

    IF batch_count < warmup_batches:
        update baseline
        CONTINUE

    psi_score <- PSI(...)

    dist_zscore <- ...

    window.add(mean_dist)

    adwin_flagged <- window.detect_change()

    drift_detected <- (
        psi_score > 0.2 OR
        abs(dist_zscore) > 3 OR
        adwin_flagged
    )

    IF NOT drift_detected:
        update baseline

    ELSE:
        alert
        retrain/refit
        reset baseline/window
"""

from __future__ import annotations

import json
import math
import threading
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
from sklearn.cluster import MiniBatchKMeans

try:
    from river.drift import ADWIN
except ImportError:
    ADWIN = None

from ..config import (
    ALPHA,
    BATCH_SIZE,
    FEATURE_DIMENSION,
    INITIAL_BUFFER_SIZE,
    K,
    K_SIGMA,
    PSI_EPSILON,
    PSI_THRESHOLD,
    RANDOM_STATE,
    RECENT_WINDOW_SIZE,
    VARIANCE_EPSILON,
    WARMUP_BATCHES,
)


class AdaptiveWindow:
    """
    Adaptive change detection window.

    River ADWIN is used when available.

    A lightweight fallback detector is also provided so that
    the module does not completely fail if river is unavailable.
    """

    def __init__(self, delta: float = 0.002):
        self.delta = delta
        self.values = deque(maxlen=RECENT_WINDOW_SIZE)

        if ADWIN is not None:
            self.adwin = ADWIN(delta=delta)
        else:
            self.adwin = None

        self._drift_detected = False

    def add(self, value: float) -> None:
        value = float(value)

        self.values.append(value)

        if self.adwin is not None:
            self.adwin.update(value)
            self._drift_detected = bool(
                self.adwin.drift_detected
            )

        else:
            self._drift_detected = self._fallback_detect()

    def _fallback_detect(self) -> bool:
        """
        Simple fallback detector.

        Compares the mean of the first and second half
        of the recent window.
        """

        if len(self.values) < 20:
            return False

        values = np.asarray(self.values, dtype=np.float64)

        midpoint = len(values) // 2

        first = values[:midpoint]
        second = values[midpoint:]

        first_mean = np.mean(first)
        second_mean = np.mean(second)

        variance = np.var(values)

        if variance < VARIANCE_EPSILON:
            return False

        difference = abs(second_mean - first_mean)

        threshold = 3.0 * math.sqrt(variance)

        return difference > threshold

    def detect_change(self) -> bool:
        return self._drift_detected

    def reset(self) -> None:
        self.values.clear()

        if ADWIN is not None:
            self.adwin = ADWIN(delta=self.delta)

        self._drift_detected = False


class AdaptiveThreatPatternClusterer:
    """
    Core Module 14 implementation.
    """

    def __init__(
        self,
        n_clusters: int = K,
        alpha: float = ALPHA,
        k_sigma: float = K_SIGMA,
        warmup_batches: int = WARMUP_BATCHES,
        recent_window_size: int = RECENT_WINDOW_SIZE,
        random_state: int = RANDOM_STATE,
        model_path: Optional[str] = None,
    ):

        if n_clusters < 2:
            raise ValueError(
                "n_clusters must be at least 2."
            )

        self.n_clusters = n_clusters
        self.alpha = alpha
        self.k_sigma = k_sigma
        self.warmup_batches = warmup_batches
        self.recent_window_size = recent_window_size
        self.random_state = random_state

        self.model = MiniBatchKMeans(
            n_clusters=self.n_clusters,
            init="k-means++",
            batch_size=BATCH_SIZE,
            random_state=self.random_state,
            n_init="auto",
        )

        self.baseline_stats: Optional[Dict[str, Any]] = None
        self.baseline_var: Optional[Dict[str, Any]] = None

        self.batch_count = 0

        self.window = AdaptiveWindow()

        self.recent_features = deque(
            maxlen=self.recent_window_size
        )

        self.initial_buffer = deque(
            maxlen=INITIAL_BUFFER_SIZE
        )

        self.feature_dimension = FEATURE_DIMENSION

        self.model_initialized = False

        self.cluster_stats: Dict[int, Dict[str, Any]] = {}

        self.last_drift = False

        self.lock = threading.Lock()

        if model_path is None:
            model_path = str(
                Path(__file__).resolve().parent /
                "m14_cluster_state.joblib"
            )

        self.model_path = model_path

        self._load_state()

    # ---------------------------------------------------------
    # MODEL INITIALIZATION
    # ---------------------------------------------------------

    def _initialize_model(
        self,
        X: np.ndarray
    ) -> None:

        if X.ndim != 2:
            raise ValueError(
                "X must be a 2D matrix."
            )

        self.feature_dimension = X.shape[1]

        self.model = MiniBatchKMeans(
            n_clusters=self.n_clusters,
            init="k-means++",
            batch_size=max(BATCH_SIZE, self.n_clusters),
            random_state=self.random_state,
            n_init="auto",
        )

        self.model.partial_fit(X)

        self.model_initialized = True

    # ---------------------------------------------------------
    # PREPROCESS
    # ---------------------------------------------------------

    def preprocess(
        self,
        X: List[List[float]]
    ) -> np.ndarray:

        if not X:
            raise ValueError(
                "Input batch cannot be empty."
            )

        matrix = np.asarray(
            X,
            dtype=np.float64
        )

        if matrix.ndim != 2:
            raise ValueError(
                "Feature vectors must be a 2D matrix."
            )

        if not np.all(np.isfinite(matrix)):
            raise ValueError(
                "Feature vectors contain NaN or infinite values."
            )

        if self.feature_dimension is None:
            self.feature_dimension = matrix.shape[1]

        if matrix.shape[1] != self.feature_dimension:
            raise ValueError(
                f"Feature dimension mismatch. "
                f"Expected {self.feature_dimension}, "
                f"received {matrix.shape[1]}."
            )

        return matrix

    # ---------------------------------------------------------
    # DISTANCE CALCULATION
    # ---------------------------------------------------------

    def distance_to_assigned_centroid(
        self,
        X: np.ndarray,
        labels: np.ndarray
    ) -> np.ndarray:

        centroids = self.model.cluster_centers_

        assigned_centroids = centroids[labels]

        distances = np.linalg.norm(
            X - assigned_centroids,
            axis=1
        )

        return distances

    # ---------------------------------------------------------
    # CLUSTER DISTRIBUTION
    # ---------------------------------------------------------

    def cluster_proportions(
        self,
        labels: np.ndarray
    ) -> List[float]:

        counts = np.bincount(
            labels,
            minlength=self.n_clusters
        )

        total = len(labels)

        if total == 0:
            return [
                0.0
                for _ in range(self.n_clusters)
            ]

        return (
            counts / total
        ).tolist()

    # ---------------------------------------------------------
    # BATCH STATISTICS
    # ---------------------------------------------------------

    def calculate_batch_stats(
        self,
        dists: np.ndarray,
        labels: np.ndarray
    ) -> Dict[str, Any]:

        return {
            "mean_dist": float(
                np.mean(dists)
            ),

            "cluster_dist": self.cluster_proportions(
                labels
            ),

            "sample_count": int(
                len(dists)
            ),
        }

    # ---------------------------------------------------------
    # EWMA
    # ---------------------------------------------------------

    def update_ewma(
        self,
        baseline: Optional[Dict[str, Any]],
        batch_stats: Dict[str, Any]
    ) -> Dict[str, Any]:

        if baseline is None:
            return {
                "mean_dist": batch_stats["mean_dist"],
                "cluster_dist": list(
                    batch_stats["cluster_dist"]
                ),
            }

        old_mean = baseline["mean_dist"]
        new_mean = batch_stats["mean_dist"]

        updated_mean = (
            (1 - self.alpha) * old_mean
            + self.alpha * new_mean
        )

        old_distribution = np.asarray(
            baseline["cluster_dist"],
            dtype=np.float64
        )

        new_distribution = np.asarray(
            batch_stats["cluster_dist"],
            dtype=np.float64
        )

        updated_distribution = (
            (1 - self.alpha) * old_distribution
            + self.alpha * new_distribution
        )

        return {
            "mean_dist": float(updated_mean),

            "cluster_dist": updated_distribution.tolist(),
        }

    # ---------------------------------------------------------
    # EWMA VARIANCE
    # ---------------------------------------------------------

    def update_ewma_variance(
        self,
        baseline_var: Optional[Dict[str, Any]],
        batch_stats: Dict[str, Any],
        baseline_stats: Dict[str, Any]
    ) -> Dict[str, Any]:

        current_value = batch_stats["mean_dist"]

        baseline_mean = baseline_stats["mean_dist"]

        squared_error = (
            current_value - baseline_mean
        ) ** 2

        if baseline_var is None:
            variance = squared_error
        else:
            old_variance = baseline_var["mean_dist"]

            variance = (
                (1 - self.alpha) * old_variance
                + self.alpha * squared_error
            )

        variance = max(
            float(variance),
            VARIANCE_EPSILON
        )

        return {
            "mean_dist": variance
        }

    # ---------------------------------------------------------
    # PSI
    # ---------------------------------------------------------

    def population_stability_index(
        self,
        actual: List[float],
        expected: List[float]
    ) -> float:

        actual_array = np.asarray(
            actual,
            dtype=np.float64
        )

        expected_array = np.asarray(
            expected,
            dtype=np.float64
        )

        actual_array = np.clip(
            actual_array,
            PSI_EPSILON,
            None
        )

        expected_array = np.clip(
            expected_array,
            PSI_EPSILON,
            None
        )

        actual_array /= np.sum(actual_array)
        expected_array /= np.sum(expected_array)

        psi = np.sum(
            (
                actual_array - expected_array
            )
            *
            np.log(
                actual_array /
                expected_array
            )
        )

        return float(psi)

    # ---------------------------------------------------------
    # Z SCORE
    # ---------------------------------------------------------

    def calculate_distance_zscore(
        self,
        batch_stats: Dict[str, Any]
    ) -> float:

        if self.baseline_stats is None:
            return 0.0

        if self.baseline_var is None:
            return 0.0

        baseline_mean = (
            self.baseline_stats["mean_dist"]
        )

        variance = max(
            self.baseline_var["mean_dist"],
            VARIANCE_EPSILON
        )

        zscore = (
            batch_stats["mean_dist"]
            - baseline_mean
        ) / math.sqrt(variance)

        return float(zscore)

    # ---------------------------------------------------------
    # CLUSTER STATISTICS
    # ---------------------------------------------------------

    def update_cluster_statistics(
        self,
        X: np.ndarray,
        labels: np.ndarray,
        distances: np.ndarray
    ) -> None:

        for cluster_id in range(
            self.n_clusters
        ):

            mask = labels == cluster_id

            if not np.any(mask):
                continue

            cluster_distances = distances[mask]

            mean_distance = float(
                np.mean(cluster_distances)
            )

            variance = float(
                np.var(cluster_distances)
            )

            size = int(
                np.sum(mask)
            )

            # Higher score means more stable
            stability_score = float(
                1.0 /
                (1.0 + mean_distance)
            )

            # Distance is used as clustering error
            error_rate = float(
                mean_distance
            )

            self.cluster_stats[cluster_id] = {
                "cluster_id": cluster_id,
                "size": size,
                "centroid": (
                    self.model.cluster_centers_[
                        cluster_id
                    ].tolist()
                ),
                "mean_distance": mean_distance,
                "distance_variance": variance,
                "stability_score": stability_score,
                "error_rate": error_rate,
            }

    # ---------------------------------------------------------
    # RETRAIN
    # ---------------------------------------------------------

    def retrain_or_refit(
        self,
        X_recent_window: np.ndarray
    ) -> None:

        if (
            X_recent_window is None
            or len(X_recent_window) < self.n_clusters
        ):
            return

        self.model = MiniBatchKMeans(
            n_clusters=self.n_clusters,
            init="k-means++",
            batch_size=max(
                BATCH_SIZE,
                self.n_clusters
            ),
            random_state=self.random_state,
            n_init="auto",
        )

        self.model.partial_fit(
            X_recent_window
        )

        self.model_initialized = True

    # ---------------------------------------------------------
    # PROCESS BATCH
    # ---------------------------------------------------------

    def process_batch(
        self,
        X_input: List[List[float]],
        entity_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:

        with self.lock:

            X = self.preprocess(X_input)

            number_of_entities = len(X)

            if entity_ids is None:
                entity_ids = [
                    f"entity_{i}"
                    for i in range(
                        number_of_entities
                    )
                ]

            if len(entity_ids) != number_of_entities:
                raise ValueError(
                    "entity_ids length must match "
                    "the number of feature vectors."
                )

            # -------------------------------------------------
            # FIRST MODEL INITIALIZATION
            # -------------------------------------------------

            if not self.model_initialized:

                for row in X:
                    self.initial_buffer.append(
                        row.tolist()
                    )

                initial_X = np.asarray(
                    self.initial_buffer,
                    dtype=np.float64
                )

                if len(initial_X) < self.n_clusters:

                    return {
                        "status": "buffering",
                        "message": (
                            "Waiting for enough feature "
                            "vectors to initialize KMeans."
                        ),
                        "required": self.n_clusters,
                        "received": len(initial_X),
                        "cluster_assignments": [],
                    }

                self._initialize_model(
                    initial_X
                )

                self.initial_buffer.clear()

            # -------------------------------------------------
            # INCREMENTAL KMEANS
            # -------------------------------------------------

            self.model.partial_fit(X)

            labels = self.model.predict(X)

            distances = (
                self.distance_to_assigned_centroid(
                    X,
                    labels
                )
            )

            # -------------------------------------------------
            # RECENT FEATURE WINDOW
            # -------------------------------------------------

            for row in X:
                self.recent_features.append(
                    row.tolist()
                )

            # -------------------------------------------------
            # BATCH STATISTICS
            # -------------------------------------------------

            batch_stats = (
                self.calculate_batch_stats(
                    distances,
                    labels
                )
            )

            # -------------------------------------------------
            # ADWIN WINDOW
            # -------------------------------------------------

            self.window.add(
                batch_stats["mean_dist"]
            )

            adwin_flagged = (
                self.window.detect_change()
            )

            # -------------------------------------------------
            # WARMUP
            # -------------------------------------------------

            if self.batch_count < self.warmup_batches:

                self.baseline_stats = (
                    self.update_ewma(
                        self.baseline_stats,
                        batch_stats
                    )
                )

                self.baseline_var = (
                    self.update_ewma_variance(
                        self.baseline_var,
                        batch_stats,
                        self.baseline_stats
                    )
                )

                self.batch_count += 1

                self.update_cluster_statistics(
                    X,
                    labels,
                    distances
                )

                self._save_state()

                return self._build_response(
                    entity_ids,
                    labels,
                    distances,
                    drift_detected=False,
                    psi_score=0.0,
                    dist_zscore=0.0,
                    adwin_flagged=adwin_flagged,
                )

            # -------------------------------------------------
            # PSI
            # -------------------------------------------------

            psi_score = (
                self.population_stability_index(
                    batch_stats["cluster_dist"],
                    self.baseline_stats[
                        "cluster_dist"
                    ]
                )
            )

            # -------------------------------------------------
            # Z SCORE
            # -------------------------------------------------

            dist_zscore = (
                self.calculate_distance_zscore(
                    batch_stats
                )
            )

            # -------------------------------------------------
            # DRIFT DECISION
            # -------------------------------------------------

            drift_detected = bool(
                psi_score > PSI_THRESHOLD
                or
                abs(dist_zscore) > self.k_sigma
                or
                adwin_flagged
            )

            self.last_drift = drift_detected

            # -------------------------------------------------
            # NORMAL OPERATION
            # -------------------------------------------------

            if not drift_detected:

                self.baseline_stats = (
                    self.update_ewma(
                        self.baseline_stats,
                        batch_stats
                    )
                )

                self.baseline_var = (
                    self.update_ewma_variance(
                        self.baseline_var,
                        batch_stats,
                        self.baseline_stats
                    )
                )

                self.batch_count += 1

            # -------------------------------------------------
            # DRIFT
            # -------------------------------------------------

            else:

                recent_X = np.asarray(
                    self.recent_features,
                    dtype=np.float64
                )

                self.retrain_or_refit(
                    recent_X
                )

                self.baseline_stats = None
                self.baseline_var = None

                self.window.reset()

                self.batch_count = 0

            # -------------------------------------------------
            # UPDATE CLUSTER STATISTICS
            # -------------------------------------------------

            self.update_cluster_statistics(
                X,
                labels,
                distances
            )

            self._save_state()

            return self._build_response(
                entity_ids,
                labels,
                distances,
                drift_detected,
                psi_score,
                dist_zscore,
                adwin_flagged,
            )

    # ---------------------------------------------------------
    # RESPONSE
    # ---------------------------------------------------------

    def _build_response(
        self,
        entity_ids,
        labels,
        distances,
        drift_detected,
        psi_score,
        dist_zscore,
        adwin_flagged,
    ) -> Dict[str, Any]:

        assignments = []

        for i, entity_id in enumerate(
            entity_ids
        ):

            cluster_id = int(
                labels[i]
            )

            assignments.append({
                "entity_id": entity_id,

                "cluster_id": cluster_id,

                "distance": float(
                    distances[i]
                ),

                "centroid": (
                    self.model.cluster_centers_[
                        cluster_id
                    ].tolist()
                ),

                "cluster_statistics":
                    self.cluster_stats.get(
                        cluster_id,
                        {}
                    ),

                "drift_detected":
                    bool(drift_detected),

                "psi_score":
                    float(psi_score),

                "dist_zscore":
                    float(dist_zscore),

                "adwin_flagged":
                    bool(adwin_flagged),
            })

        return {
            "status": "success",

            "batch_count":
                self.batch_count,

            "drift_detected":
                bool(drift_detected),

            "psi_score":
                float(psi_score),

            "dist_zscore":
                float(dist_zscore),

            "adwin_flagged":
                bool(adwin_flagged),

            "cluster_assignments":
                assignments,

            "cluster_statistics":
                list(
                    self.cluster_stats.values()
                ),

            "centroids":
                self.model.cluster_centers_.tolist(),

        }

    # ---------------------------------------------------------
    # STATE SAVE
    # ---------------------------------------------------------

    def _save_state(self) -> None:

        state = {
            "model": self.model,
            "baseline_stats":
                self.baseline_stats,
            "baseline_var":
                self.baseline_var,
            "batch_count":
                self.batch_count,
            "feature_dimension":
                self.feature_dimension,
            "cluster_stats":
                self.cluster_stats,
            "model_initialized":
                self.model_initialized,
        }

        try:
            Path(
                self.model_path
            ).parent.mkdir(
                parents=True,
                exist_ok=True
            )

            joblib.dump(
                state,
                self.model_path
            )

        except Exception:
            # Persistence failure should not stop
            # real-time clustering.
            pass

    # ---------------------------------------------------------
    # STATE LOAD
    # ---------------------------------------------------------

    def _load_state(self) -> None:

        path = Path(
            self.model_path
        )

        if not path.exists():
            return

        try:

            state = joblib.load(
                path
            )

            self.model = state["model"]

            self.baseline_stats = (
                state.get(
                    "baseline_stats"
                )
            )

            self.baseline_var = (
                state.get(
                    "baseline_var"
                )
            )

            self.batch_count = (
                state.get(
                    "batch_count",
                    0
                )
            )

            self.feature_dimension = (
                state.get(
                    "feature_dimension"
                )
            )

            self.cluster_stats = (
                state.get(
                    "cluster_stats",
                    {}
                )
            )

            self.model_initialized = (
                state.get(
                    "model_initialized",
                    False
                )
            )

        except Exception:
            self.model_initialized = False

    # ---------------------------------------------------------
    # RESET
    # ---------------------------------------------------------

    def reset(self) -> None:

        with self.lock:

            self.model = MiniBatchKMeans(
                n_clusters=self.n_clusters,
                init="k-means++",
                batch_size=BATCH_SIZE,
                random_state=self.random_state,
                n_init="auto",
            )

            self.baseline_stats = None
            self.baseline_var = None

            self.batch_count = 0

            self.window.reset()

            self.recent_features.clear()

            self.initial_buffer.clear()

            self.cluster_stats = {}

            self.model_initialized = False

            self.last_drift = False

            path = Path(
                self.model_path
            )

            if path.exists():
                try:
                    path.unlink()
                except Exception:
                    pass

    # ---------------------------------------------------------
    # CURRENT STATISTICS
    # ---------------------------------------------------------

    def get_statistics(self) -> Dict[str, Any]:

        response = {
            "model_initialized":
                self.model_initialized,

            "feature_dimension":
                self.feature_dimension,

            "n_clusters":
                self.n_clusters,

            "batch_count":
                self.batch_count,

            "warmup_batches":
                self.warmup_batches,

            "baseline_stats":
                self.baseline_stats,

            "baseline_variance":
                self.baseline_var,

            "last_drift":
                self.last_drift,

            "cluster_statistics":
                list(
                    self.cluster_stats.values()
                ),
        }

        if self.model_initialized:
            response["centroids"] = (
                self.model.cluster_centers_
                .tolist()
            )

        else:
            response["centroids"] = []

        return response


# -------------------------------------------------------------
# SINGLE SERVICE INSTANCE
# -------------------------------------------------------------

cluster_service = AdaptiveThreatPatternClusterer()