# M13_cross_modal_feature_standardization/algorithms/__init__.py

"""
Module 13 Standardization Algorithm
"""

import math
from typing import Dict, List, Any

from ..config import (
    COMMON_FEATURE_SCHEMA,
    DEFAULT_MISSING_VALUE
)


def collect_modality_features(
    module_outputs: Dict[str, Dict[str, Any]]
) -> Dict[str, float]:

    """
    Collect numerical features from all detector modules.
    """

    collected_features = {}

    if not module_outputs:
        return collected_features

    for modality, features in module_outputs.items():

        if not isinstance(features, dict):
            continue

        for feature_name, value in features.items():

            try:

                if value is None:
                    continue

                numeric_value = float(value)

                if not math.isfinite(numeric_value):
                    continue

                collected_features[feature_name] = numeric_value

            except (ValueError, TypeError):

                # Ignore non-numeric detector outputs
                continue

    return collected_features


def map_to_common_schema(
    raw_features: Dict[str, float]
) -> Dict[str, float]:

    """
    Converts heterogeneous detector outputs
    into the common M13 schema.
    """

    common_features = {}

    for feature_name in COMMON_FEATURE_SCHEMA:

        if feature_name in raw_features:

            common_features[feature_name] = (
                raw_features[feature_name]
            )

        else:

            common_features[feature_name] = None

    return common_features


def handle_missing_features(
    common_features: Dict[str, Any]
):

    """
    Handles missing detector features consistently.
    """

    filled_features = {}

    missing_features = []

    for feature_name in COMMON_FEATURE_SCHEMA:

        value = common_features.get(feature_name)

        if value is None:

            filled_features[feature_name] = (
                DEFAULT_MISSING_VALUE
            )

            missing_features.append(feature_name)

        else:

            try:

                numeric_value = float(value)

                if not math.isfinite(numeric_value):

                    numeric_value = (
                        DEFAULT_MISSING_VALUE
                    )

                    missing_features.append(
                        feature_name
                    )

                filled_features[feature_name] = (
                    numeric_value
                )

            except (ValueError, TypeError):

                filled_features[feature_name] = (
                    DEFAULT_MISSING_VALUE
                )

                missing_features.append(
                    feature_name
                )

    return filled_features, missing_features


def create_feature_vector(
    filled_features: Dict[str, float]
) -> List[float]:

    """
    Creates fixed-length FeatureVector[N].
    """

    feature_vector = []

    for feature_name in COMMON_FEATURE_SCHEMA:

        value = filled_features.get(
            feature_name,
            DEFAULT_MISSING_VALUE
        )

        feature_vector.append(float(value))

    return feature_vector