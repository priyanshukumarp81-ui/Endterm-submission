import os

# Configuration & Constants
LOG_DIR = "logs"
OUTPUT_DIR = "output"
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Bounded Action Set
ACTIONS = {
    "NO_ACTION": "No action required - signals below threshold.",
    "PROACTIVE_RETENTION": "Proactive retention outreach (discount, fee waiver, loyalty gesture).",
    "RM_ESCALATION": "Relationship-manager escalation for high-value / nuanced situations.",
    "PERSONALIZED_OFFER": "Pre-approved product offer (loan, credit line, investment).",
    "SUPPORT_INTERVENTION": "Proactive support/service intervention to resolve brewing issues.",
    "COMPLIANCE_HOLD": "Compliance or fraud hold pending human review."
}

# Guardrail Keywords (Deterministic bypasses)
LEGAL_THREAT_KEYWORDS = ["lawsuit", "legal action", "attorney", "court", "sue", "ombudsman", "consumer forum"]
FRAUD_KEYWORDS = ["fraud", "stolen", "unauthorized transfer", "account takeover", "phishing", "scam"]