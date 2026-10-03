from guardrails import GuardrailsEngine

class BaseAgent:
    def __init__(self, name: str):
        self.name = name

class UsageEngagementAgent(BaseAgent):
    def __init__(self):
        super().__init__("Usage/Engagement Agent")

    def analyze(self, event: dict, state_board) -> dict:
        event_type = event.get("event_type", event.get("type"))
        data = event.get("payload", event.get("data", {}))
        
        # Web app events ya login events ko handle karein
        if event_type in ["app_usage", "login", "feature_used", "session_duration"]:
            login_drop = data.get("login_frequency_drop_pct", 0)
            trend = "high_drop" if login_drop >= 30 else "normal"
            state_board.update_working_memory("login_frequency_trend", f"{login_drop}% drop")
            return {"agent": self.name, "finding": f"Login frequency/usage drop detected: {login_drop}%", "risk_flag": trend == "high_drop"}
        return {"agent": self.name, "finding": "No usage anomalies detected.", "risk_flag": False}
    
class SupportSentimentAgent(BaseAgent):
    def __init__(self):
        super().__init__("Support/Sentiment Agent")

    def analyze(self, event: dict, state_board) -> dict:
        event_type = event.get("event_type", event.get("type"))
        data = event.get("payload", event.get("data", {}))
        
        # Support tickets ya call transcripts ko handle karein
        if event_type in ["support_ticket", "ticket_created", "call_transcript", "life_event_mention"]:
            ticket_text = data.get("raw_text", data.get("text", ""))
            sentiment = data.get("sentiment", "neutral")
            guardrail_check = GuardrailsEngine.check_guardrails(ticket_text)
            state_board.update_working_memory("support_sentiment", sentiment)
            return {
                "agent": self.name, 
                "finding": f"Support sentiment: {sentiment}. Text: {GuardrailsEngine.mask_pii(ticket_text[:50])}", 
                "risk_flag": sentiment in ["negative", "furious"],
                "guardrail_override": guardrail_check
            }
        return {"agent": self.name, "finding": "No support events.", "risk_flag": False}
    
class TransactionBillingAgent(BaseAgent):
    def __init__(self):
        super().__init__("Transaction/Billing Agent")

    def analyze(self, event: dict, state_board) -> dict:
        event_type = event.get("event_type", event.get("type"))
        data = event.get("payload", event.get("data", {}))
        
        # Card payments, transfers, ya ledger transactions ko handle karein
        if event_type in ["transaction", "card_transaction", "inbound_transfer", "outbound_transfer", "deposit", "withdrawal"]:
            amount = data.get("amount", 0)
            is_anomaly = data.get("is_anomaly", False) or amount > 10000  # Example heuristic for large amounts
            state_board.update_working_memory("transaction_anomaly_score", 0.9 if is_anomaly else 0.1)
            return {"agent": self.name, "finding": f"Transaction amount: ${amount}, Anomaly: {is_anomaly}", "risk_flag": is_anomaly}
        return {"agent": self.name, "finding": "No transaction events.", "risk_flag": False}
    
class LifeEventInferenceAgent(BaseAgent):
    def __init__(self):
        super().__init__("Life-Event Inference Agent")

    def analyze(self, state_board) -> dict:
        findings = state_board.swarm_findings
        # Check cross-signal correlation e.g. large deposit + home loan app search
        has_large_txn = any("Transaction" in k and "Anomaly" in str(v) for k, v in findings.items())
        state_board.set_life_phase("Potential Major Life Event (Property/Relocation)")
        return {"agent": self.name, "inferred_life_event": state_board.inferred_life_phase}

class SynthesisCorrelationAgent(BaseAgent):
    def __init__(self):
        super().__init__("Synthesis/Correlation Agent")

    def synthesize(self, state_board) -> dict:
        return {
            "agent": self.name,
            "summary": f"Customer {state_board.customer_id} state synthesized.",
            "life_phase": state_board.inferred_life_phase,
            "working_memory": state_board.working_memory
        }

class RetentionActionAgent(BaseAgent):
    def __init__(self):
        super().__init__("Retention/Action Agent")

    def decide_action(self, synthesis_output: dict, state_board) -> tuple:
    # 1. Guardrail check sabse pehle
        for agent_name, finding in state_board.swarm_findings.items():
            if isinstance(finding, dict) and finding.get("guardrail_override", {}).get("triggered"):
                override = finding["guardrail_override"]
                return override["action"], override["reason"], True

        # 2. Get incoming event details
        recent_events = state_board.working_memory.get("recent_events", [])
        latest_event = recent_events[-1] if recent_events else {}
        payload = latest_event.get("payload", {})
        event_type = latest_event.get("event_type", "")
        merchant = str(payload.get("merchant_name", "")).lower()

        # Agar normal everyday purchase hai (jaise Starbucks, Amazon, etc.), toh NO_ACTION do!
        if event_type == "purchase" and any(m in merchant for m in ["starbucks", "amazon", "uber", "netflix"]):
            return "NO_ACTION", "Routine everyday transaction; no proactive intervention needed.", False

        # 3. Life phase checks (only if specific severe signals exist)
        life_phase = str(state_board.inferred_life_phase).lower()
        
        if "medical" in life_phase or "hardship" in life_phase:
            return "SUPPORT_INTERVENTION", "Detected medical hardship or financial distress requiring payment plan.", True
        elif "property" in life_phase or "relocation" in life_phase:
            # Sirf tabhi offer do jab loan ya mortgage jaisa event ho, har choti shopping par nahi!
            if "mortgage" in merchant or "bank" in merchant or event_type == "loan_application":
                return "PERSONALIZED_OFFER", "Customer showing genuine mortgage/property signals; offering tailored financial products.", False

        # 4. Sentiment & Login trends
        login_trend = state_board.working_memory.get("login_frequency_trend", "stable")
        sentiment = state_board.working_memory.get("support_sentiment", "neutral")
        
        if "drop" in login_trend and sentiment in ["negative", "furious"]:
            return "PROACTIVE_RETENTION", "High churn risk due to dropped engagement and negative support sentiment.", False
        elif sentiment in ["negative", "furious"]:
            return "SUPPORT_INTERVENTION", "Support intervention needed due to negative sentiment.", False
        
        # Default fallback
        return "NO_ACTION", "Signals are within normal acceptable baseline thresholds.", False