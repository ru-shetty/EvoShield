import numpy as np

from ..services.service import (
    AdaptiveThreatPatternClusterer,
)


def make_batch(
    center,
    size=30,
    dimension=10
):

    return np.random.normal(
        loc=center,
        scale=0.05,
        size=(size, dimension)
    ).tolist()


def test_incremental_partial_fit():

    service = AdaptiveThreatPatternClusterer(
        n_clusters=3,
        warmup_batches=3
    )

    for _ in range(5):

        X = make_batch(
            center=0.0
        )

        result = service.process_batch(
            X
        )

        assert result is not None

    assert service.model_initialized


def test_statistics_endpoint_data():

    service = AdaptiveThreatPatternClusterer(
        n_clusters=3
    )

    X = make_batch(
        center=0.0
    )

    service.process_batch(X)

    statistics = (
        service.get_statistics()
    )

    assert (
        statistics["model_initialized"]
        is True
    )

    assert (
        statistics["n_clusters"]
        == 3
    )

    assert (
        len(statistics["centroids"])
        == 3
    )


def test_reset():

    service = AdaptiveThreatPatternClusterer(
        n_clusters=3
    )

    X = make_batch(
        center=0.0
    )

    service.process_batch(X)

    service.reset()

    assert (
        service.model_initialized
        is False
    )

    assert service.batch_count == 0

    assert (
        service.baseline_stats
        is None
    )

    assert (
        service.baseline_var
        is None
    )