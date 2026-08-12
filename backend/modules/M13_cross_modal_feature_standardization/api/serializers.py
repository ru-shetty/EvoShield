# M13_cross_modal_feature_standardization/api/serializers.py

from rest_framework import serializers


class CrossModalFeatureInputSerializer(
    serializers.Serializer
):

    entity_id = serializers.CharField(
        required=True
    )

    url = serializers.DictField(
        required=False,
        allow_null=True
    )

    nlp = serializers.DictField(
        required=False,
        allow_null=True
    )

    ocr = serializers.DictField(
        required=False,
        allow_null=True
    )

    speech = serializers.DictField(
        required=False,
        allow_null=True
    )

    malware = serializers.DictField(
        required=False,
        allow_null=True
    )

    digital_arrest = serializers.DictField(
        required=False,
        allow_null=True
    )


class CrossModalFeatureOutputSerializer(
    serializers.Serializer
):

    EntityID = serializers.CharField()

    FeatureVector = serializers.ListField(
        child=serializers.FloatField()
    )

    FeatureVectorSize = serializers.IntegerField()

    PreprocessingVersion = serializers.CharField()

    SchemaVersion = serializers.CharField()

    MissingFeatures = serializers.ListField(
        child=serializers.CharField()
    )

    Timestamp = serializers.CharField()