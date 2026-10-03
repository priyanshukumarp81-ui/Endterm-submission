class CustomerStateBoard:
    """
    Shared per-customer state board acting as working and episodic memory.
    Every agent writes its structured findings here; downstream agents read from it.
    """
    def __init__(self, customer_id: str):
        self.customer_id = customer_id
        self.working_memory = {
            "recent_events": [],
            "login_frequency_trend": "stable",
            "support_sentiment": "neutral",
            "transaction_anomaly_score": 0.0,
            "kyc_status": "verified"
        }
        self.inferred_life_phase = "baseline"
        self.episodic_history = []
        self.swarm_findings = {}

    def update_working_memory(self, key: str, value):
        self.working_memory[key] = value

    def record_event(self, event: dict):
        self.working_memory["recent_events"].append(event)
        # Keep last 10 events in working memory
        if len(self.working_memory["recent_events"]) > 10:
            self.working_memory["recent_events"].pop(0)

    def publish_finding(self, agent_name: str, findings: dict):
        self.swarm_findings[agent_name] = findings

    def add_episodic_record(self, record: str):
        self.episodic_history.append(record)

    def set_life_phase(self, phase: str):
        self.inferred_life_phase = phase