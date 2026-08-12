# M13_cross_modal_feature_standardization/api/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    CrossModalFeatureInputSerializer
)

from ..services.service import (
    CrossModalFeatureService
)

from ..models.models import (
    StandardizedFeatureVector
)


class CrossModalFeatureStandardizationView(
    APIView
):

    """
    POST endpoint for Module 13.

    Receives detector outputs from
    different EvoShield modules.
    """

    def post(self, request):

        serializer = (
            CrossModalFeatureInputSerializer(
                data=request.data
            )
        )

        if not serializer.is_valid():

            return Response(
                {
                    "success": False,
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data

        entity_id = data.pop(
            "entity_id"
        )

        # Remaining data contains modalities
        module_outputs = data

        try:

            service = (
                CrossModalFeatureService()
            )

            result = service.standardize(
                entity_id=entity_id,
                module_outputs=module_outputs
            )

            # Save to database

            StandardizedFeatureVector.objects.create(

                entity_id=result["EntityID"],

                feature_vector=result[
                    "FeatureVector"
                ],

                feature_vector_size=result[
                    "FeatureVectorSize"
                ],

                preprocessing_version=result[
                    "PreprocessingVersion"
                ],

                schema_version=result[
                    "SchemaVersion"
                ],

                missing_features=result[
                    "MissingFeatures"
                ]
            )

            return Response(
                {
                    "success": True,
                    "module": (
                        "M13_CrossModalFeatureStandardization"
                    ),
                    "data": result
                },
                status=status.HTTP_200_OK
            )

        except FileNotFoundError as error:

            return Response(
                {
                    "success": False,
                    "error": str(error)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as error:

            return Response(
                {
                    "success": False,
                    "error": str(error)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )