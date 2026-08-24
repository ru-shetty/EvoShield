class MonitoringDashboardEngine:

    def generate_dashboard(self, monitoring_data):

        dashboard = {
            "overview": {},
            "scans": {},
            "threats": {},
            "risk": {},
            "clusters": {},
            "drift": {},
            "rollback": {},
            "history": {},
            "notifications": []
        }

        dashboard["overview"] = {
            "system_status": "ACTIVE",
            "module": "M11 Security Monitoring"
        }

        dashboard["scans"] = {
            "total_scans": monitoring_data.get("total_scans", 0)
        }

        dashboard["threats"] = {
            "active_threats": monitoring_data.get("active_threats", 0)
        }

        dashboard["risk"] = {
            "risk_level": monitoring_data.get("risk_level", "LOW")
        }

        dashboard["clusters"] = {
            "cluster_count": monitoring_data.get("cluster_count", 0)
        }

        dashboard["drift"] = {
            "drift_events": monitoring_data.get("drift_events", 0)
        }

        dashboard["rollback"] = {
            "rollback_events": monitoring_data.get("rollback_events", 0)
        }

        dashboard["history"] = {
            "history_records": monitoring_data.get("history_records", 0)
        }

        dashboard["notifications"] = monitoring_data.get(
            "notifications",
            []
        )

        return dashboard


if __name__ == "__main__":

    sample_data = {
        "total_scans": 120,
        "active_threats": 5,
        "risk_level": "HIGH",
        "cluster_count": 3,
        "drift_events": 1,
        "rollback_events": 0,
        "history_records": 250,
        "notifications": [
            "Malware alert detected",
            "Digital arrest warning detected"
        ]
    }

    engine = MonitoringDashboardEngine()

    result = engine.generate_dashboard(sample_data)

    print(result)