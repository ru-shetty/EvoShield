import numpy as np

import pytest

from rest_framework.test import APIClient


@pytest.mark.django_db
def test_process_api():

    client = APIClient()

    feature_vectors = []

    for i in range(20):

        features = np.random.normal(
            0,
            0.1,
            10
        ).tolist()

        feature_vectors.append({
            "entity_id": f"entity_{i}",
            "features": features,
        })

    response = client.post(
        "/api/m14/process/",
        {
            "feature_vectors":
                feature_vectors
        },
        format="json"
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        "cluster_assignments"
        in data
    )


@pytest.mark.django_db
def test_statistics_api():

    client = APIClient()

    response = client.get(
        "/api/m14/statistics/"
    )

    assert response.status_code == 200