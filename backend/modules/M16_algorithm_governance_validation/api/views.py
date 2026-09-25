import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..services.service import GovernanceService


governance_service = GovernanceService()


@csrf_exempt
def create_candidate(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST required"},
            status=405,
        )

    try:
        data = json.loads(
            request.body.decode("utf-8")
        )

        candidate = governance_service.create_candidate(
            model_version=data["model_version"],
            preprocessor_version=data[
                "preprocessor_version"
            ],
            cluster_version=data[
                "cluster_version"
            ],
            drift_parameter_version=data[
                "drift_parameter_version"
            ],
            parameters=data.get(
                "parameters",
                {},
            ),
            metadata=data.get(
                "metadata",
                {},
            ),
        )

        return JsonResponse({
            "status": "candidate_created",
            "version": candidate.version_id(),
        })

    except Exception as exc:

        return JsonResponse(
            {"error": str(exc)},
            status=400,
        )


@csrf_exempt
def deploy_candidate(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST required"},
            status=405,
        )

    try:
        data = json.loads(
            request.body.decode("utf-8")
        )

        candidate = governance_service.create_candidate(
            model_version=data["model_version"],
            preprocessor_version=data[
                "preprocessor_version"
            ],
            cluster_version=data[
                "cluster_version"
            ],
            drift_parameter_version=data[
                "drift_parameter_version"
            ],
            parameters=data.get(
                "parameters",
                {},
            ),
        )

        result = governance_service.deploy_candidate(
            candidate,
            data["validation_data"],
        )

        return JsonResponse(result)

    except Exception as exc:

        return JsonResponse(
            {"error": str(exc)},
            status=400,
        )


@csrf_exempt
def runtime_event(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST required"},
            status=405,
        )

    try:
        data = json.loads(
            request.body.decode("utf-8")
        )

        governance_service.record_runtime_event(
            confidence=data["confidence"],
            error=data.get("error", False),
            drift=data.get("drift", False),
            rollback=data.get(
                "rollback",
                False,
            ),
            false_positive=data.get(
                "false_positive",
                False,
            ),
            reanalysis_success=data.get(
                "reanalysis_success",
                True,
            ),
            trust_score=data.get(
                "trust_score",
                1.0,
            ),
        )

        return JsonResponse({
            "status": "recorded",
            "health": (
                governance_service.health_status()
            ),
        })

    except Exception as exc:

        return JsonResponse(
            {"error": str(exc)},
            status=400,
        )


def health(request):

    if request.method != "GET":
        return JsonResponse(
            {"error": "GET required"},
            status=405,
        )

    return JsonResponse(
        governance_service.health_status()
    )


@csrf_exempt
def rollback(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST required"},
            status=405,
        )

    return JsonResponse(
        governance_service.rollback()
    )


@csrf_exempt
def attach_versions(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST required"},
            status=405,
        )

    try:

        data = json.loads(
            request.body.decode("utf-8")
        )

        result = governance_service.attach_versions(
            data
        )

        return JsonResponse(result)

    except Exception as exc:

        return JsonResponse(
            {"error": str(exc)},
            status=400,
        )