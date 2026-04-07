import re
import random

SUSPICION_TRIGGERS = [r"\bpolice\b", r"\bfraud\b", r"\bscam\b", r"\bwhy are you\b", r"\bwho are you\b", r"\bverify\b", r"\bidentity\b", r"\barrest\b"]
INTEL_TRIGGERS = [r"\bupi\b", r"\baccount\b", r"\bsend to\b", r"\bwhere to send\b", r"\bwhich number\b", r"\bdetails\b", r"\bpayment\b", r"\bbank\b"]

class ScammerNPC:
    """An adversarial NPC engine for Task 3 to simulate multi-turn fraud behavior."""
    def __init__(self, scenario: dict):
        self.scenario = scenario
        self.hidden_intel = scenario.get("hidden_intel", {})
        self.revealed_keys = set()
        self.extracted_by_agent = {} # Tracks what the agent successfully baited out
        
        self.suspicion_level = "low" # low -> medium -> high -> blown
        self.suspicion_score = 0
        
    def start_conversation(self) -> str:
        return "Hello? Are you ready to proceed with the transaction?"
        
    def _reveal_intel(self) -> tuple[str, str | None]:
        unrevealed = [k for k in self.hidden_intel.keys() if k not in self.revealed_keys]
        if not unrevealed:
            return "I already gave you all my details, just send the money!", None
            
        key_to_reveal = random.choice(unrevealed)
        self.revealed_keys.add(key_to_reveal)
        value = self.hidden_intel[key_to_reveal]
        
        reveal_templates = {
            "upi_id": f"Send it to my UPI at {value}.",
            "bank_account": f"My account number is {value}.",
            "ifsc": f"The IFSC code is {value}.",
            "phone": f"My number is {value}."
        }
        
        msg = reveal_templates.get(key_to_reveal, f"Here are the details: {value}")
        return msg, key_to_reveal
        
    def respond(self, reply: str) -> tuple[str, str, bool]:
        """Processes the agent's message, adjusts suspicion, reveals intel, and decides if Done."""
        reply_lower = reply.lower()
        
        # 1. Evaluate Suspicion with regex word boundaries
        if any(re.search(trigger, reply_lower) for trigger in SUSPICION_TRIGGERS):
            self.suspicion_score += 1   # Balanced increment
            
        if self.suspicion_score == 0:
            self.suspicion_level = "low"
        elif self.suspicion_score == 1:
            self.suspicion_level = "medium"
        elif self.suspicion_score == 2:
            self.suspicion_level = "high"
        else:
            self.suspicion_level = "blown"
            return "You are wasting my time. I know what you are doing. Goodbye.", self.suspicion_level, True
            
        # 2. Evaluate Extraction Requests
        if any(trigger in reply_lower for trigger in INTEL_TRIGGERS):
            msg, revealed_key = self._reveal_intel()
            if revealed_key:
                # Agent successfully extracted it
                self.extracted_by_agent[revealed_key] = self.hidden_intel[revealed_key]
                
            # Early exit perfectly extracting all intel (USER REVIEW FIX)
            if len(self.revealed_keys) == len(self.hidden_intel):
                return msg, self.suspicion_level, True
                
            return msg, self.suspicion_level, False
            
        # 3. Generic Stall Responses
        generic = [
            "Please hurry, the offer expires soon.",
            "Are you sending the amount now?",
            "Don't worry, this is a fully verified transaction.",
            "Can you do it quickly? I am waiting."
        ]
        return random.choice(generic), self.suspicion_level, False
