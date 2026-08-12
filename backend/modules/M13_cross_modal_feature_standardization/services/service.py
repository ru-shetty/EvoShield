# M13_cross_modal_feature_standardization/services/service.py

from ..processors.processor import (
    CrossModalFeatureProcessor
)


class CrossModalFeatureService:

    """
    Service layer for Module 13.
    """

    def __init__(self):

        self.processor = (
            CrossModalFeatureProcessor()
        )

    def standardize(
        self,
        entity_id,
        module_outputs
    ):

        """
        Standardize outputs received from
        different EvoShield modules.
        """

        if not entity_id:

            raise ValueError(
                "EntityID is required."
            )

        if not isinstance(
            module_outputs,
            dict
        ):

            raise ValueError(
                "module_outputs must be a dictionary."
            )

        return self.processor.process(
            entity_id=entity_id,
            module_outputs=module_outputs
        )

    def train_scaler(
        self,
        training_vectors
    ):

        """
        Train and save the preprocessing scaler.
        """

        return self.processor.fit_scaler(
            training_vectors
        )