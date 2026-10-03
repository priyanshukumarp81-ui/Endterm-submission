import re
from config import LEGAL_THREAT_KEYWORDS, FRAUD_KEYWORDS

class GuardrailsEngine:
    @staticmethod
    def check_guardrails(text_content: str) -> dict:
        """
        Deterministic, hard-coded safety net that intercepts legal threats, 
        fraud flags, or severe risks, bypassing standard agent autonomy.
        """
        if not text_content:
            return {"triggered": False, "action": None, "reason": None}
            
        lower_text = text_content.lower()
        
        # Check legal threats
        for kw in LEGAL_THREAT_KEYWORDS:
            if re.search(r'\b' + re.escape(kw) + r'\b', lower_text):
                return {
                    "triggered": True, 
                    "action": "COMPLIANCE_HOLD", 
                    "reason": f"Guardrail triggered: Legal threat keyword detected ('{kw}'). Route to Legal Escalation."
                }
                
        # Check fraud keywords
        for kw in FRAUD_KEYWORDS:
            if re.search(r'\b' + re.escape(kw) + r'\b', lower_text):
                return {
                    "triggered": True, 
                    "action": "COMPLIANCE_HOLD", 
                    "reason": f"Guardrail triggered: Fraud keyword detected ('{kw}'). Freeze account & route to Fraud Ops."
                }
                
        return {"triggered": False, "action": None, "reason": None}

    @staticmethod
    def mask_pii(text: str) -> str:
        """Masks sensitive PII like account numbers, SSNs, or phone numbers in logs/prompts."""
        if not text:
            return ""
        # Mask 12-16 digit account numbers
        text = re.sub(r'\b\d{12,16}\b', '[REDACTED_ACCOUNT]', text)
        # Mask Phone numbers
        text = re.sub(r'\b\+?\d{10,12}\b', '[REDACTED_PHONE]', text)
        return text