import numpy as np

from ..services.service import (
    AdaptiveThreatPatternClusterer,
)


def generate_normal_batch(
    size=20,
    dimension=10
):

    return np.random.normal(
        loc=0.0,
        scale=0.1,
        size=(size, dimension)
    ).tolist()


def generate_drift_batch(
    size=20,
    dimension=10
):

    return np.random.normal(
        loc=5.0,
        scale=0.1,
        size=(size, dimension)
    ).tolist()


def test_cluster_initialization():

    service = AdaptiveThreatPatternClusterer(
        n_clusters=3,
        warmup_batches=2,
        recent_window_size=100
    )

    X = generate_normal_batch(
        size=20,
        dimension=10
    )

    result = service.process_batch(X)

    assert service.model_initialized is True

    assert len(
        result["cluster_assignments"]
    ) == 20


def test_every_entity_gets_cluster_id():

    service = AdaptiveThreatPatternClusterer(
        n_clusters=3,
        warmup_batches=2
    )

    X = generate_normal_batch(
        size=20,
        dimension=10
    )

    result = service.process_batch(
        X
    )

    assignments = (
        result["cluster_assignments"]
    )

    assert len(assignments) == 20

    for assignment in assignments:

        assert (
            assignment["cluster_id"]
            is not None
        )

        assert (
            assignment["distance"]
            >= 0
        )


def test_centroids_are_generated():

    service = AdaptiveThreatPatternClusterer(
        n_clusters=3
    )

    X = generate_normal_batch(
        size=20,
        dimension=10
    )

    result = service.process_batch(X)

    centroids = result["centroids"]

    assert len(centroids) == 3

    assert len(centroids[0]) == 10


def test_cluster_statistics():

    service = AdaptiveThreatPatternClusterer(
        n_clusters=3
    )

    X = generate_normal_batch(
        size=30,
        dimension=10
    )

    result = service.process_batch(X)

    statistics = (
        result["cluster_statistics"]
    )

    assert len(statistics) > 0

    for cluster in statistics:

        assert "cluster_id" in cluster
        assert "size" in cluster
        assert "centroid" in cluster
        assert "mean_distance" in cluster
        assert "distance_variance" in cluster
        assert "stability_score" in cluster
        assert "error_rate" in cluster


def test_batch_statistics_and_baseline():

    service = AdaptiveThreatPatternClusterer(
        n_clusters=3,
        warmup_batches=3
    )

    for _ in range(3):

        X = generate_normal_batch(
            size=20,
            dimension=10
        )

        result = service.process_batch(X)

    assert service.baseline_stats is not None

    assert service.baseline_var is not None


 #test code

def test_drift_detection():

    service = AdaptiveThreatPatternClusterer(
        n_clusters=3,
        warmup_batches=5,
        recent_window_size=100
    )

    # -----------------------------
    # Phase 1: Normal data
    # -----------------------------

    for _ in range(8):

        X = np.random.normal(
            loc=0.0,
            scale=0.05,
            size=(30, 10)
        ).tolist()

        result = service.process_batch(X)

        print(
            "\nNormal batch"
        )

        print(
            "PSI:",
            result["psi_score"]
        )

        print(
            "Z-score:",
            result["dist_zscore"]
        )

        print(
            "ADWIN:",
            result["adwin_flagged"]
        )

        print(
            "Drift:",
            result["drift_detected"]
        )

    # -----------------------------
    # Phase 2: Drift data
    # -----------------------------

    drift_found = False

    for _ in range(10):

        X = np.random.normal(
            loc=5.0,
            scale=0.05,
            size=(30, 10)
        ).tolist()

        result = service.process_batch(X)

        print(
            "\nDrift batch"
        )

        print(
            "PSI:",
            result["psi_score"]
        )

        print(
            "Z-score:",
            result["dist_zscore"]
        )

        print(
            "ADWIN:",
            result["adwin_flagged"]
        )

        print(
            "Drift:",
            result["drift_detected"]
        )

        if result["drift_detected"]:
            drift_found = True
            break

    assert drift_found is True 


#test
def test_drift_triggers_retraining_and_reset():

    service = AdaptiveThreatPatternClusterer(
        n_clusters=3,
        warmup_batches=3,
        recent_window_size=100
    )

    # ---------------------------------------
    # Phase 1: Build normal baseline
    # ---------------------------------------

    for _ in range(6):

        X = np.random.normal(
            loc=0.0,
            scale=0.05,
            size=(30, 10)
        ).tolist()

        result = service.process_batch(X)

    # Baseline should exist
    assert service.baseline_stats is not None
    assert service.baseline_var is not None

    old_model = service.model
    old_batch_count = service.batch_count

    # ---------------------------------------
    # Phase 2: Introduce strong distribution drift
    # ---------------------------------------

    drift_X = np.random.normal(
        loc=5.0,
        scale=0.05,
        size=(30, 10)
    ).tolist()

    result = service.process_batch(drift_X)

    # ---------------------------------------
    # Verify drift was detected
    # ---------------------------------------

    assert result["drift_detected"] is True

    # ---------------------------------------
    # Verify model was retrained/refitted
    # ---------------------------------------

    assert service.model_initialized is True

    assert service.model is not old_model

    # ---------------------------------------
    # Verify baseline was reset
    # ---------------------------------------

    assert service.baseline_stats is None
    assert service.baseline_var is None

    # ---------------------------------------
    # Verify batch counter was reset
    # ---------------------------------------

    assert service.batch_count == 0

    # ---------------------------------------
    # Verify window was reset
    # ---------------------------------------

    assert len(service.window.values) == 0

#test
def test_drift_triggers_retraining_and_reset():

    service = AdaptiveThreatPatternClusterer(
        n_clusters=3,
        warmup_batches=3,
        recent_window_size=100
    )

    # ---------------------------------------
    # Phase 1: Build normal baseline
    # ---------------------------------------

    for _ in range(6):

        X = np.random.normal(
            loc=0.0,
            scale=0.05,
            size=(30, 10)
        ).tolist()

        service.process_batch(X)

    # Baseline must exist
    assert service.baseline_stats is not None
    assert service.baseline_var is not None

    # Keep reference to the current model
    old_model = service.model

    # ---------------------------------------
    # Phase 2: Introduce strong drift
    # ---------------------------------------

    drift_X = np.random.normal(
        loc=5.0,
        scale=0.05,
        size=(30, 10)
    ).tolist()

    result = service.process_batch(drift_X)

    # ---------------------------------------
    # 1. Drift detected
    # ---------------------------------------

    assert result["drift_detected"] is True

    # ---------------------------------------
    # 2. Model still initialized
    # ---------------------------------------

    assert service.model_initialized is True

    # ---------------------------------------
    # 3. Model was replaced/retrained
    # ---------------------------------------

    assert service.model is not old_model

    # ---------------------------------------
    # 4. Baseline reset
    # ---------------------------------------

    assert service.baseline_stats is None
    assert service.baseline_var is None

    # ---------------------------------------
    # 5. Batch counter reset
    # ---------------------------------------

    assert service.batch_count == 0

    # ---------------------------------------
    # 6. Adaptive window reset
    # ---------------------------------------

    assert len(service.window.values) == 0

    # ---------------------------------------
    # 7. ADWIN state reset
    # ---------------------------------------

    assert service.window.detect_change() is False      