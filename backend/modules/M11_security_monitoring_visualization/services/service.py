from ..processors.processor import MonitoringProcessor
from ..algorithms.monitoring_dashboard_engine import MonitoringDashboardEngine
from ..schemas.schemas import MonitoringSchema


def run_service(data):

    processor = MonitoringProcessor()
    processed_data = processor.process(data)

    validation = MonitoringSchema.validate(processed_data)

    engine = MonitoringDashboardEngine()
    dashboard = engine.generate_dashboard(processed_data)

    return {
        "module": "M11",
        "input_type": "monitoring_data",
        "validation": validation,
        "result": dashboard
    }


if __name__ == "__main__":

    sample_input = {
        "total_scans": 100,
        "active_threats": 4,
        "risk_level": "HIGH",
        "cluster_count": 2,
        "drift_events": 1,
        "rollback_events": 0,
        "history_records": 200,
        "notifications": [
            "Threat detected",
            "Risk increased"
        ]
    }

    print(run_service(sample_input))