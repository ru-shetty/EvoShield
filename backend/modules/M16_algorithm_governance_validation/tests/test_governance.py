from modules.M16_adaptive_algorithm_governance_and_validation.services.service import (
    GovernanceService,
)


def valid_validation_data():

    return {
        "expected_schema": {
            "features": [
                "url_score",
                "nlp_score",
                "ocr_score",
                "speech_score",
            ]
        },

        "candidate_schema": {
            "features": [
                "url_score",
                "nlp_score",
                "ocr_score",
                "speech_score",
            ]
        },

        "model_metadata": {
            "scaler_version": "S1",
            "encoder_version": "E1",
        },

        "preprocessing_metadata": {
            "scaler_version": "S1",
            "encoder_version": "E1",
        },

        "detector_metrics": {
            "accuracy": 0.90,
            "error_rate": 0.10,
        },

        "clustering_metrics": {
            "stability": 0.90,
        },

        "drift_metrics": {
            "drift_rate": 0.10,
            "rollback_rate": 0.05,
        },

        "audit_config": {
            "enabled": True,
        },

        "parameters": {
            "threshold": 0.5,
        },

        "parameter_ranges": {
            "threshold": {
                "min": 0.1,
                "max": 0.9,
            }
        },
    }


def test_candidate_is_approved():

    service = GovernanceService()

    candidate = service.create_candidate(
        model_version="M1",
        preprocessor_version="P1",
        cluster_version="C1",
        drift_parameter_version="D1",
    )

    result = service.deploy_candidate(
        candidate,
        valid_validation_data(),
    )

    assert result["decision"] == "approve_and_deploy"
    assert result["validation_status"] == "passed"

    assert service.registry.active() is candidate


def test_bad_candidate_is_rejected():

    service = GovernanceService()

    candidate = service.create_candidate(
        model_version="M2",
        preprocessor_version="P2",
        cluster_version="C2",
        drift_parameter_version="D2",
    )

    data = valid_validation_data()

    data["detector_metrics"]["accuracy"] = 0.30

    result = service.deploy_candidate(
        candidate,
        data,
    )

    assert result["decision"] == "reject"
    assert candidate.status == "rejected"


def test_previous_version_is_preserved():

    service = GovernanceService()

    first = service.create_candidate(
        "M1",
        "P1",
        "C1",
        "D1",
    )

    service.deploy_candidate(
        first,
        valid_validation_data(),
    )

    second = service.create_candidate(
        "M2",
        "P2",
        "C2",
        "D2",
    )

    service.deploy_candidate(
        second,
        valid_validation_data(),
    )

    assert (
        service.previous_approved_version
        == first.version_id()
    )


def test_rollback():

    service = GovernanceService()

    first = service.create_candidate(
        "M1",
        "P1",
        "C1",
        "D1",
    )

    service.deploy_candidate(
        first,
        valid_validation_data(),
    )

    second = service.create_candidate(
        "M2",
        "P2",
        "C2",
        "D2",
    )

    service.deploy_candidate(
        second,
        valid_validation_data(),
    )

    result = service.rollback()

    assert result["decision"] == "rollback"

    assert (
        service.registry.active()
        is first
    )


def test_runtime_monitoring():

    service = GovernanceService()

    for _ in range(5):

        service.record_runtime_event(
            confidence=0.90,
            error=False,
            drift=False,
            rollback=False,
            false_positive=False,
            reanalysis_success=True,
            trust_score=0.90,
        )

    health = service.health_status()

    assert health["metrics"]["confidence"] == 0.90
    assert health["metrics"]["error_rate"] == 0.0
    assert health["metrics"]["drift_frequency"] == 0.0
    assert health["healthy"] is True


def test_versions_attached_to_analysis():

    service = GovernanceService()

    candidate = service.create_candidate(
        "M1",
        "P1",
        "C1",
        "D1",
    )

    service.deploy_candidate(
        candidate,
        valid_validation_data(),
    )

    record = {
        "analysis_id": "A001",
        "risk_score": 0.85,
    }

    result = service.attach_versions(record)

    assert result["versions"]["model_version"] == "M1"
    assert result["versions"]["preprocessor_version"] == "P1"
    assert result["versions"]["cluster_version"] == "C1"
    assert result["versions"]["drift_parameter_version"] == "D1"