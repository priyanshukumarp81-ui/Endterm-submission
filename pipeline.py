import json
import os
from datetime import datetime
from config import OUTPUT_DIR, LOG_DIR
from memory import CustomerStateBoard
from agents import (
    UsageEngagementAgent, 
    SupportSentimentAgent, 
    TransactionBillingAgent, 
    LifeEventInferenceAgent, 
    SynthesisCorrelationAgent, 
    RetentionActionAgent
)

class Customer360Orchestrator:
    def __init__(self):
        self.usage_agent = UsageEngagementAgent()
        self.support_agent = SupportSentimentAgent()
        self.txn_agent = TransactionBillingAgent()
        self.life_agent = LifeEventInferenceAgent()
        self.synth_agent = SynthesisCorrelationAgent()
        self.action_agent = RetentionActionAgent()
        
        self.audit_logs = []
        self.inferred_events_records = []

    def process_event_stream(self, events: list):
        if not events:
            return
            
        # Customer ID extract karein (assume karte hain stream same customer ki hai)
        customer_id = events[0].get("customer_id", "CUST_DEFAULT")
        
        # State board ko loop ke BAHAR banayein taaki history accumulate ho sake!
        state_board = CustomerStateBoard(customer_id)

        for idx, event in enumerate(events):
            state_board.record_event(event)

            # Event ke andar jo actual time diya ho, use prioritize karein
            timestamp = event.get("event_time") or event.get("timestamp") or datetime.utcnow().isoformat()

            # 1. Swarm Stage (Parallel independent agent reads)
            usage_res = self.usage_agent.analyze(event, state_board)
            state_board.publish_finding(self.usage_agent.name, usage_res)

            support_res = self.support_agent.analyze(event, state_board)
            state_board.publish_finding(self.support_agent.name, support_res)

            txn_res = self.txn_agent.analyze(event, state_board)
            state_board.publish_finding(self.txn_agent.name, txn_res)

            # 2. Life Event Inference
            life_res = self.life_agent.analyze(state_board)

            # 3. Synthesis Stage
            synth_res = self.synth_agent.synthesize(state_board)

            # 4. Action & Guardrail Check
            action, explanation, guardrail_triggered = self.action_agent.decide_action(synth_res, state_board)

            # Record Traceability Log
            trace_entry = {
                "step": idx + 1,
                "timestamp": timestamp,
                "customer_id": customer_id,
                "incoming_event": event,
                "swarm_findings": state_board.swarm_findings,
                "inferred_life_phase": state_board.inferred_life_phase,
                "decided_action": action,
                "explainability_reason": explanation,
                "guardrail_triggered": guardrail_triggered
            }
            self.audit_logs.append(trace_entry)

            # Required Schema for Evaluation Artifact (`inferred-events`)
            self.inferred_events_records.append({
                "timestamp": timestamp,
                "customer_id": customer_id,
                "inferred_customer_state": {
                    "life_phase": state_board.inferred_life_phase,
                    "working_memory": state_board.working_memory.copy() # Safe copy of working memory
                },
                "confidence_level": "high" if guardrail_triggered or action != "NO_ACTION" else "medium",
                "action_decided": action,
                "explanation": explanation
            })

        self.save_artifacts()

    def save_artifacts(self):
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save Audit Trail
        audit_path = os.path.join(LOG_DIR, f"audit_trail_{timestamp_str}.json")
        with open(audit_path, "w") as f:
            json.dump(self.audit_logs, f, indent=4)
            
        # Save Inferred Events Schema (Mandatory Deliverable)
        inferred_path = os.path.join(OUTPUT_DIR, f"inferred_events_{timestamp_str}.json")
        with open(inferred_path, "w") as f:
            json.dump(self.inferred_events_records, f, indent=4)
            
        print(f"\n[INFO] Pipeline execution complete!")
        print(f"[INFO] Audit logs saved to: {audit_path}")
        print(f"[INFO] Inferred events artifact saved to: {inferred_path}")