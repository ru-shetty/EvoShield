from ..processors.processor import SecurityDataProcessor
from ..algorithms.security_data_audit_engine import SecurityDataAuditEngine
from ..schemas.schemas import SecurityAuditSchema


def run_service(data):

    processor = SecurityDataProcessor()

    processed_data = processor.process(data)

    engine = SecurityDataAuditEngine()

    audit_record = engine.store_security_record(
        processed_data
    )

    validation = SecurityAuditSchema.validate(
        processed_data
    )

    return {
        "module": "M12",
        "input_type": "security_audit_data",
        "validation": validation,
        "result": audit_record
    }


if __name__ == "__main__":

    sample_input = {
        "entity_id": "ENT001",
        "entity_type": "URL",
        "feature_vector": [0.3, 0.5, 0.8],
        "cluster_id": 2,
        "trust_level": 85,
        "status": "SAFE",
        "risk_history": [20, 25, 15],
        "drift_events": [],
        "rollback_logs": [],
        "model_name": "EvoShield",
        "model_version": "1.0",
        "analysis_version": "12.0"
    }

    print(run_service(sample_input))