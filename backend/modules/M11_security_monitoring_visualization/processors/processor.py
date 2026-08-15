class MonitoringProcessor:

    def process(self, raw_data):

        processed_data = {
            "total_scans": raw_data.get("total_scans", 0),
            "active_threats": raw_data.get("active_threats", 0),
            "risk_level": raw_data.get("risk_level", "LOW"),
            "cluster_count": raw_data.get("cluster_count", 0),
            "drift_events": raw_data.get("drift_events", 0),
            "rollback_events": raw_data.get("rollback_events", 0),
            "history_records": raw_data.get("history_records", 0),
            "notifications": raw_data.get("notifications", [])
        }

        return processed_data


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

    processor = MonitoringProcessor()

    result = processor.process(sample_input)

    print(result)