"""
Processor for Module 14.

Input:
    Normalized FeatureVector[N]

Output:
    NumPy matrix suitable for MiniBatchKMeans.
"""

from typing import List, Tuple

import numpy as np

from ..config import FEATURE_DIMENSION


class FeatureVectorProcessor:

    def __init__(self):
        self.feature_dimension = FEATURE_DIMENSION

    def preprocess(
        self,
        feature_vectors: List[List[float]]
    ) -> Tuple[np.ndarray, int]:
        """
        Validate and convert normalized feature vectors
        into a numeric NumPy matrix.
        """

        if not feature_vectors:
            raise ValueError("Feature vector batch cannot be empty.")

        try:
            X = np.asarray(feature_vectors, dtype=np.float64)
        except Exception as exc:
            raise ValueError(
                f"Unable to convert feature vectors to numeric matrix: {exc}"
            )

        if X.ndim != 2:
            raise ValueError(
                "Feature vectors must form a 2-dimensional matrix."
            )

        if X.shape[0] == 0:
            raise ValueError("Batch contains no samples.")

        if X.shape[1] == 0:
            raise ValueError("Feature vectors contain zero features.")

        if not np.all(np.isfinite(X)):
            raise ValueError(
                "Feature vectors contain NaN or infinite values."
            )

        current_dimension = X.shape[1]

        # Automatically learn dimension from first batch
        if self.feature_dimension is None:
            self.feature_dimension = current_dimension

        # Make sure all vectors have the same dimension
        if current_dimension != self.feature_dimension:
            raise ValueError(
                f"Invalid feature dimension. "
                f"Expected {self.feature_dimension}, "
                f"received {current_dimension}."
            )

        return X, current_dimension

    def preprocess_single(
        self,
        features: List[float]
    ) -> np.ndarray:
        """
        Preprocess one feature vector.
        """

        X, _ = self.preprocess([features])

        return X